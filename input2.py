{
    number = 33;
    isPrime = 1;
    i = 2;
    while(i<number && isPrime==1) {
        if (number%i==0) {
       	    isPrime = 0;
        }
     i = i + 1;
    }
    if(isPrime==1){
        print("isPrime is true");
    } else {
        print("isPrime is false");
    }
}