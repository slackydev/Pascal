function Main(lim:Int):Boolean;
var
 i,a: Int;
 b:Float;
begin
  print('Starting:',lim);

  a := 1594;
  for i:= 0 to lim do
  begin
    //b := a*0.333333333
    //b := a*0.5
    b := a/3
    b := a/2
  end;
end;


begin
  var a := main(50000000);
end; 