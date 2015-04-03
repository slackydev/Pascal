var i:Int;
begin
  for i:=0 to 1000 do
  begin
    break;
    print 'Break failed!'
  end;
  print 'Break:   ',i = 0
  
  for i:=0 to 1000 do
  begin
    continue;
    print 'Continue failed!'
  end;
  print 'Continue:',i = 1000
  
  for i:=0 to 1000 do
  begin
    pass;
    print 'Pass failed!'
  end;
  print 'Pass:    ',i = 1000
end.