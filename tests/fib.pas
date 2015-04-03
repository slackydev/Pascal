function fibonacci(n:Int): Int
begin
  if(n = 0) then
    Exit(0)
  else if(n = 1) then
    Exit(1)
  else
    Exit(fibonacci(n - 1) + fibonacci(n - 2))
end;

begin
  print fibonacci(33)
end.
