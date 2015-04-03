var 
  n, k: Int; 
  is_prime: Bool;
begin
  n := 1;
  var primes := 0
  var lim := 5000000
  while n < lim do
  begin  
    k := 3
    is_prime := True; 
    n += 2
    while k * k <= n and is_prime do 
    begin
      is_prime := n div k * k != n; 
      k += 2
    end;
    if is_prime then
      primes += 1
  end;
end;