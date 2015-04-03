type
  TIntArray = Array of Int;

function Swap(ref x,y:Int);
begin
  var tmp := x;
  x := y;
  y := tmp;
end;  
  
function InsSort(ref Arr:TIntArray; left,right:Int);
begin
  for var i:=left+1 to right do 
  begin
    var j := i-1;
    var Tmp := arr[i];
    while (j >= left) and (Arr[j] > Tmp) do 
    begin
      Arr[j+1] := Arr[j];
      j:=j-1;
    end;
    Arr[j+1] := Tmp;
  end;
end;

function QuickSort(ref Arr:TIntArray; left, right:Int);
var i,j,pivot:Int;
begin
  if (left + 20 <= right) then 
  begin
    i:=left;
    j:=right;
    pivot := Arr[(left+right) shr 1];
    repeat
      while pivot > Arr[i] do i+=1;
      while pivot < Arr[j] do j-=1;
      if i<=j then 
      begin
        Swap(Arr[i],Arr[j]);
        {var tmp := Arr[i];
        Arr[i] := Arr[j];
        Arr[j] := tmp;}
        j-=1;
        i+=1;
      end;
    until (i>j);

    if (left < j) then QuickSort(Arr, left, j);
    if (i < right) then QuickSort(Arr, i, right);
  end else
    InsSort(Arr, left, right);
end;
 
function ShellSort(ref Arr: TIntArray);
var
  i,j,H: Int;
begin
  H := Length(Arr);
  var Gap := 0;
  while (Gap < H div 3) do 
    Gap := Gap * 3 + 1;
  while Gap >= 1 do 
  begin
    for i:=Gap to H do 
    begin
      j := i;
      while (j >= Gap) and (Arr[j] < Arr[j - Gap]) do
      begin
        var tmp := Arr[j];
        Arr[j] := Arr[j - Gap];
        Arr[j - Gap] := tmp;
        j -= Gap;
      end;
    end;
    Gap /= 3;
  end;
end;
 
function NewTest(n:Int): TIntArray;
begin
  SetLength(Result, n)
  for var i:=0 to n do 
    Result[i] := RandInt(0,$FFFFFF)
end;

var a:TIntArray;
begin
  for var i:=0 to 10 do
  begin
    a := NewTest(1000000);
    var t := time()
    QuickSort(a,0,High(a))
    //ShellSort(a)
    //Sort(a)
    print(time() - t)
  end;
end;