type
  TPoint = record x,y:Int32 end
  TStruct = record 
    id:Int  
    pt:TPoint 
  end
 
var
  n: Int
  p: TPoint
  s: TStruct
end //alternative `end` to allow loose statements
 
p.x := 55
p.y := 1
s.pt := p
s.id := 170
print p,', ', s
 
type T = Int end
print 'Works'
 
type Double = Float
begin
  var F := -1013.3
  print 'Also works,', Abs(F)
end.
