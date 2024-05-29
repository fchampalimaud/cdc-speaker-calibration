function x = noise(sigma,n)

range=1; 

c=1/(sqrt(2)*sigma);
cdfinv = @(y) erfinv(y*2*erf(c*range) + erf(-c*range))/(c);
x=cdfinv(rand(1,n));

% disp(['std = ',num2str(std(x))])
% disp(['mean = ',num2str(mean(x))])

% figure(1)
% hist(x,64);