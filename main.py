# Geoffrey Churchill    108902941

import tpg

class Parser(tpg.Parser): # we can enable l-value array indexing by having it bind more tightly than '='
    r"""
    # Options
    set lexer_dotall = True
    #set lexer_verbose = True
    
    token real  : '\d+\.\d*|\.\d+'        RealLiteral;
    token int   : '\d+'                   IntLiteral;
    token string: '".*?"'                 StringLiteral;
    token ident : '[A-Za-z][A-Za-z0-9_]*' IdentLiteral;
    
    token o00: '(?<![\=\!\<\>])=(?![\=\!\<\>])' $ getOp
    token o01: 'or'                $ getOp
    token o02: '(and)|(&&)'        $ getOp
    token o03: 'not'               $ getOp
    token o04: '(<=|==|<>|>=|<|>)' $ getOp
    token o05: 'in'                $ getOp
    token o06: '(\+|-)'            $ getOp
    token o07: '//'                $ getOp
    token o08: '\*\*'              $ getOp
    token o09: '%'                 $ getOp
    token o10:'(\*|/)'             $ getOp
    ;
    
    separator whitespace '\s+';
    separator comment    '(#.*?\n)|(@.*?@)';
    
    START/a -> expression/a;
    
    expression/a -> l00/a;
    l00/a ->(((ident/a list/b $a = IdentLiteral((a, b))$) | ident/a) o00/op expression/b $a.isLHS = True; a = op(a, b)$) | # '=' is left-associative
             l01/a;
    l01/a -> l02/a (o01/op l02/b $a = op(a, b)$)*;
    l02/a -> l03/a (o02/op l03/b $a = op(a, b)$)*;
    l03/a -> (o03/op l03/a $a = op(a   )$)|l04/a ;
    l04/a -> l05/a (o04/op l05/b $a = op(a, b)$)*;
    l05/a -> l06/a (o05/op l06/b $a = op(a, b)$)*;
    l06/a -> l07/a (o06/op l07/b $a = op(a, b)$)*;
    l07/a -> l08/a (o07/op l08/b $a = op(a, b)$)*;
    l08/a -> l09/a (o08/op l09/b $a = op(a, b)$)*;
    l09/a -> l10/a (o09/op l10/b $a = op(a, b)$)*;
    l10/a -> l11/a (o10/op l11/b $a = op(a, b)$)*;
    l11/a -> l12/a (list/b $a = getOp('index')(a,b)$)*;
    l12/a -> literal/a | ('\(' expression/a '\)');
    
    commasep/a -> $a = []$ (expression/b $a.append(b)$ (',' expression/b $a.append(b)$)*)?;
    
    block/a -> '{' $a = []$ ((funcblockblock/b | funcblock/b | (expression/b ';')) $a.append(b)$ )* '}' $a = BlockLiteral(a)$;

    function/a -> ident/a '\(' commasep/b '\)' $a = FunctionLiteral(a, b)$;
    
    funcblock/a -> ident/a '\(' expression/e '\)' block/b $a = FunctionBlockLiteral(a, e, b)$;

    funcblockblock/a -> ident/a '\(' expression/e '\)' block/b1 ident/i2 block/b2 $a = FunctionBlockBlockLiteral(a, e, b1, i2, b2)$;
    
    list/a -> "\[" commasep/a "\]" $a = ListLiteral(a)$;
    
    literal/a -> funcblockblock/a | funcblock/a | block/a | function/a | real/a | int/a | string/a | list/a | ident/a;
    """

class Context(dict):
            def __init__(self):
                self.parent = None

            def __missing__(self, key):
                return self.parent[key]

            def update(self, other=None, **kwargs):
                for key, val in other.items():
                    cur = self
                    while cur is not None:
                        if key in cur:
                            cur[key] = val
                            return
                        cur = cur.parent
                        self[key] = val

            def __repr__(self):
                return repr((dict.__repr__(self),str(self.parent)))
            
class SemanticError(Exception):
    pass

class Node(object):
    def evaluate(self, context):
        """
        Called on children of Node to evaluate that child.
        """
        raise Exception("Not implemented.")
    
class IntLiteral(Node):
    def __init__(self, value):
        self.value = int(value)

    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return repr(self.value)

class RealLiteral(Node):
    def __init__(self, value):
        from decimal import Decimal
        Decimal = float # this is just here to meet the assignment description        
        self.value = Decimal(value)

    def evaluate(self, context):
        return self.value

class StringLiteral(Node):
    def __init__(self, value):
        self.value = value[1:-1]
        
    def evaluate(self, context):
        return self.value

    def __repr__(self):
        return '"'+self.value+'"'

class BlockLiteral(Node):
    def __init__(self, value):
        self.context = Context()
        self.value = list(value) # TODO is cast necessary?

    def evaluate(self, parent):
        self.context.parent = parent
        for statement in self.value[:-1]:
            statement.evaluate(self.context)
        if len(self.value):
            return self.value[-1].evaluate(self.context) # returns result of last statement

    def __repr__(self):
        return 'block:'+repr(self.value)

class FunctionLiteral(Node):
    def __init__(self, ident, args):
        self.ident = ident
        self.args = args
        
    def evaluate(self, context):
        return self.ident.evaluate(context)(*(a.evaluate(context) for a in self.args))

    def __repr__(self):
        return 'func:'+repr(self.ident)+'('+repr(self.args)+')'

class FunctionBlockLiteral(Node):
    def __init__(self, ident, head, body):
        self.ident = ident
        self.head = head
        self.body = body

    def evaluate(self, context):
        self.ident.evaluate(context)(self.head, self.body, context)

    def __repr__(self):
        return 'funcblock:'+repr(self.ident)+'('+repr(self.head)+')'+repr(self.body)

class FunctionBlockBlockLiteral(Node):
    def __init__(self, ident1, head, body1, ident2, body2):
        self.ident = IdentLiteral((ident1.name, ident2.name))
        self.head = head
        self.body1, self.body2 = body1, body2

    def evaluate(self, context):
        self.ident.evaluate(context)(self.head, self.body1, self.body2, context)

    def __repr__(self):
        return 'funcblockblock:'+repr(self.ident)+'('+repr(self.head)+')'+repr(self.body2)+repr(self.body2)
    
class ListLiteral(Node):
    def __init__(self, value):
        self.value = value

    def evaluate(self, context):
        return [x.evaluate(context) for x in self.value]

    def __repr__(self):
        return 'list:'+str(self.value)
    
class IdentLiteral(Node):
    def __init__(self, name):
        self.name = name
        self.isLHS = False # assume RHS
        
    def evaluate(self, context):
        if self.isLHS:
            name = self.name
            if type(name) is tuple:
                def setListElement(val):
                    self.name[0].evaluate(context)[self.name[1].evaluate(context)[0]] = val
                return lambda val: setListElement(val)
            else:
                return lambda val: context.update({self.name: val})
        else:
            return context[self.name]

    def __repr__(self):
        return 'ident('+('L' if self.isLHS else 'R')+'):'+self.name
    
def makeOps():
    def makeOp(func, name):
        class OpClass(Node):
            def __init__(self, *args):
                self.args = args

            def evaluate(self, context):
                return func(*(a.evaluate(context) for a in self.args))

            def __repr__(self):
                return 'op:'+name+'('+repr(self.args)+')'
            
        OpClass.__name__ = name
        return OpClass
    
    ops = {
        'index': lambda x, y: x[y[0]],
        '*':     lambda x, y: x *  y,
        '/':     lambda x, y: x /  y,
        '%':     lambda x, y: x %  y,
        '**':    lambda x, y: x ** y,
        '//':    lambda x, y: x // y,
        '+':     lambda x, y: x +  y,
        '-':     lambda x, y: x -  y,
        'in':    lambda x, y: int(x in y),
        '<':     lambda x, y: int(x <  y),
        '<=':    lambda x, y: int(x <= y),
        '==':    lambda x, y: int(x == y),
        '<>':    lambda x, y: int(x != y),
        '>':     lambda x, y: int(x >  y),
        '>=':    lambda x, y: int(x >= y),
        'not':   lambda x   : int(not  x),
        'and':   lambda x, y: int(bool(x) and bool(y)),
        '&&':    lambda x, y: int(bool(x) and bool(y)),
        'or':    lambda x, y: int(bool(x) or bool(y)),
        '=':     lambda x, y: x(y),
    }
    
    from inspect import signature
    for key, val in ops.items():
        ops[key] = makeOp(val, name = key)
        
    global getOp
    def getOp(x):
        return ops[x]

def myWhile(cond, body, context):
    while cond.evaluate(context):
        body.evaluate(context)

def myIf(cond, body, context):
    if cond.evaluate(context):
        body.evaluate(context)
        
def myIfElse(cond, ifBody, elseBody, context):
    if cond.evaluate(context):
        ifBody.evaluate(context)
    else:
        elseBody.evaluate(context)
        
builtins = Context()
builtins.update({
    'while': myWhile,
    'if':    myIf,
    ('if','else'): myIfElse,
    'print': lambda x: print(repr(x)),
    'add':   lambda x, y: x + y,
})

if __name__ == '__main__':
    makeOps()
    parse = Parser()
    
    try:
        from sys import argv
        f = open(argv[1], "r")
    except(IndexError, IOError):
        f = open("input2.py", "r")
        
    try:
        node = parse(f.read())
        result = node.evaluate(builtins)
        print(repr(result))
        
    except tpg.Error:
        print("SYNTAX ERROR")
        # Uncomment the next line to re-raise the syntax error,
        # displaying where it occurs. Comment it for submission.
        raise
    
    except TypeError:
        print("SEMANTIC ERROR")
        # Uncomment the next line to re-raise the semantic error,
        # displaying where it occurs. Comment it for submission.
        raise
    
    f.close()
