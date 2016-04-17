{
    if(1){
        number = 337**2;
        isPrime = 1;
        i = 2;

    while(i<number && isPrime==1)
        {

        if (number%i==0)
            {
       	        isPrime = 0;
            }
            i = i + 1;
        }
        
    print(isPrime);

    if(isPrime==1)
        {
            print("isPrime is true");
        }

    else
        {
            print("isPrime is false");
        }
    }
    
    if(1)
    {

        data = [ [ 100, 42 ], [ 100, 50 ], [ 123, 456 ], [ 300, 9000 ] ];
        result = [ 0, 0, 0, 0 ];
        i = 0;

        while (i < 4){

                a = data[i][0];
                b = data[i][1];

                if (a > 0){

                        while (b > 0){

                                if (a > b){
                                        a = a - b;
                                } else {
                                    b = b - a;
                                }
                        }
                }
                print("result[");
                print(i);
                print("] =");
                print(a);
                result[i] = a;
                i = i + 1;
        }

        print(result);
    }
}
