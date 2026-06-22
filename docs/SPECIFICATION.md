# Muharram Language Specification

## Syntax Overview

### Variables

```
var x = 10
var name = "Muharram"
var pi = 3.14
```

### Classes and Properties

```
class Person
  property name
  property age
  
  method greet
    print("Hello, I am " + name)
  end
end

var person = Person()
person.name = "Alice"
person.age = 30
person.greet()
```

### Basic Data Types

- `int` - Integer numbers
- `float` - Floating point numbers
- `string` - Text strings
- `bool` - Boolean (true/false)
- `nil` - Null value

### Control Flow

```
if x > 5
  print("x is greater than 5")
else
  print("x is 5 or less")
end

while i < 10
  print(i)
  i = i + 1
end
```

### Methods

```
method add(a, b)
  return a + b
end

var result = add(3, 5)
```

## Example Program

```
class Calculator
  property result
  
  method __init
    result = 0
  end
  
  method add(x)
    result = result + x
  end
  
  method display
    print("Result: " + result)
  end
end

var calc = Calculator()
calc.add(10)
calc.add(5)
calc.display()
```
