function fibonacci(n:Int):Int;
begin
  if(n = 0) then
    Result := 0;
  else if(n = 1) then
    Result := 1;
  else
    Result := fibonacci(n - 1) + fibonacci(n - 2);
end;

begin
  print fibonacci(33)
end;