type
  TPoint = record x,y:Int32 end
  TStruct = record 
    id:Int;  
    pt:TPoint 
  end
 
var
  p: TPoint
  s: TStruct
end //gotta say that this is the end of the above block..->
 
//.. so now we can do without the "begin" and the "end"
p.x := 55
p.y := 1
s.pt := p
s.id := 170
print p,'|', s
 
type Number = Int; end
print 'Works';
 
type Double = Float;
begin
  var F := -1013.3;
  print 'Also works,', Abs(F);
end.