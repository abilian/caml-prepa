# Reference card

Everything the subset has, on one page.

!!! note "Three of these tables are generated"
    The operators, the keywords and the standard library are read off the
    compiler itself when this page is built, so they cannot fall behind it.
    The prose around them is written by hand.

## Definitions

```ocaml
let x = 42
let f x y = x + y                     (* two parameters *)
let rec fact n =                      (* rec, for a recursive call *)
  if n <= 1 then 1 else n * fact (n - 1)
let rec even n = ... and odd n = ...  (* mutual recursion *)
let () = print_int (fact 5)           (* run something *)
let a, b = 1, 2                       (* a pattern binds *)
let g x = let y = x * 2 in y + 1      (* local, with `in` *)
```

## Types

```ocaml
int  float  char  string  bool  unit  exn
'a list        'a array       'a option      'a ref
int * string                          (* a pair *)
int -> int -> int                     (* a function of two arguments *)

type colour = Red | Green | Blue
type 'a tree = Empty | Node of 'a tree * 'a * 'a tree
type point = { x : float; mutable y : float }
type number = int                     (* an alias *)
exception Empty
exception Too_big of int
```

A constructor takes one argument, and `of int * string` makes that argument a pair. `mutable` is what lets a field be assigned with `<-`.

## Expressions

```ocaml
if c then a else b                    (* both branches, same type *)
match e with | p -> a | q when g -> b
function | p -> a | q -> b            (* a function that matches *)
fun x y -> e                          (* anonymous *)
try e with Empty -> a | Failure m -> b
while c do e done
for i = 0 to n - 1 do e done          (* `downto` counts back *)
a; b                                  (* a is evaluated for its effect *)
begin a; b end                        (* the same, bracketed *)
[ 1; 2; 3 ]      1 :: rest       l1 @ l2
[| 1; 2; 3 |]    t.(i)           t.(i) <- v
s.[i]            "bon" ^ "jour"
{ x = 1.0; y = 2.0 }    p.x      p.y <- 3.0    { p with x = 0.0 }
let r = ref 0 in r := !r + 1; incr r
```

## Patterns

```ocaml
_                    x                    42        'a'       "s"
(a, b)               a :: rest            []        [ a; b ]  [| a; b |]
Node (l, v, r)      Some x               None
{ x = a; y = b }     p as whole            0 | 1 | 2
```

Every alternative of a `|` pattern has to bind the same names, and a case may carry a guard: `| n when n < 0 -> ...`.

## Operators

Tightest first. Application binds tighter than any of them, and prefix `-`, `-.` and `!` tighter still.

| level | operators | associates |
| --- | --- | --- |
| 1 | `**` `lsl` `lsr` `asr` | right |
| 2 | `*` `/` `*.` `/.` `mod` `land` `lor` `lxor` | left |
| 3 | `+` `-` `+.` `-.` | left |
| 4 | `::` | right |
| 5 | `@` `^` | right |
| 6 | `=` `<>` `<` `<=` `>` `>=` | left |
| 7 | `&&` | right |
| 8 | `\|\|` | right |

The `.` forms are for floats: `1 + 2` and `1.0 +. 2.0`, and never the two mixed. `=` is structural equality, `<>` its negation, and `:=` writes through a `ref`. Any of them can be used as a value by bracketing it, as in `List.fold_left ( + ) 0`.

## Keywords

`and` `as` `asr` `begin` `do` `done` `downto` `else` `end` `exception` `false` `for` `fun` `function` `if` `in` `land` `let` `lor` `lsl` `lsr` `lxor` `match` `mod` `mutable` `of` `rec` `then` `to` `true` `try` `type` `when` `while` `with`

## The standard library

Everything a programme may use without defining it, with the type it has. There is no `open`: a module name is a prefix.

### Always in scope

| name | type |
| --- | --- |
| `not` | `bool -> bool` |
| `ref` | `'a -> 'a ref` |
| `incr` | `int ref -> unit` |
| `decr` | `int ref -> unit` |
| `ignore` | `'a -> unit` |
| `fst` | `'a * 'b -> 'a` |
| `snd` | `'a * 'b -> 'b` |
| `compare` | `'a -> 'a -> int` |
| `min` | `'a -> 'a -> 'a` |
| `max` | `'a -> 'a -> 'a` |
| `abs` | `int -> int` |
| `succ` | `int -> int` |
| `pred` | `int -> int` |
| `raise` | `exn -> 'a` |
| `failwith` | `string -> 'a` |
| `invalid_arg` | `string -> 'a` |
| `print_int` | `int -> unit` |
| `print_float` | `float -> unit` |
| `print_char` | `char -> unit` |
| `print_string` | `string -> unit` |
| `print_endline` | `string -> unit` |
| `print_newline` | `unit -> unit` |
| `read_int` | `unit -> int` |
| `read_float` | `unit -> float` |
| `read_line` | `unit -> string` |
| `string_of_int` | `int -> string` |
| `int_of_string` | `string -> int` |
| `string_of_float` | `float -> string` |
| `float_of_string` | `string -> float` |
| `string_of_bool` | `bool -> string` |
| `bool_of_string` | `string -> bool` |
| `float_of_int` | `int -> float` |
| `int_of_float` | `float -> int` |
| `char_of_int` | `int -> char` |
| `int_of_char` | `char -> int` |
| `truncate` | `float -> int` |
| `sqrt` | `float -> float` |
| `exp` | `float -> float` |
| `log` | `float -> float` |
| `sin` | `float -> float` |
| `cos` | `float -> float` |
| `tan` | `float -> float` |
| `atan` | `float -> float` |
| `floor` | `float -> float` |
| `ceil` | `float -> float` |
| `abs_float` | `float -> float` |
| `infinity` | `float` |
| `neg_infinity` | `float` |
| `max_int` | `int` |
| `min_int` | `int` |
| `assert` | `bool -> unit` |
| `+` | `int -> int -> int` |
| `-` | `int -> int -> int` |
| `*` | `int -> int -> int` |
| `/` | `int -> int -> int` |
| `mod` | `int -> int -> int` |
| `land` | `int -> int -> int` |
| `lor` | `int -> int -> int` |
| `lxor` | `int -> int -> int` |
| `lsl` | `int -> int -> int` |
| `lsr` | `int -> int -> int` |
| `asr` | `int -> int -> int` |
| `+.` | `float -> float -> float` |
| `-.` | `float -> float -> float` |
| `*.` | `float -> float -> float` |
| `/.` | `float -> float -> float` |
| `**` | `float -> float -> float` |
| `^` | `string -> string -> string` |
| `@` | `'a list -> 'a list -> 'a list` |
| `=` | `'a -> 'a -> bool` |
| `<>` | `'a -> 'a -> bool` |
| `<` | `'a -> 'a -> bool` |
| `<=` | `'a -> 'a -> bool` |
| `>` | `'a -> 'a -> bool` |
| `>=` | `'a -> 'a -> bool` |
| `&&` | `bool -> bool -> bool` |
| `\|\|` | `bool -> bool -> bool` |
| `:=` | `'a ref -> 'a -> unit` |
| `!` | `'a ref -> 'a` |

### List

| name | type |
| --- | --- |
| `List.length` | `'a list -> int` |
| `List.hd` | `'a list -> 'a` |
| `List.tl` | `'a list -> 'a list` |
| `List.nth` | `'a list -> int -> 'a` |
| `List.rev` | `'a list -> 'a list` |
| `List.append` | `'a list -> 'a list -> 'a list` |
| `List.concat` | `'a list list -> 'a list` |
| `List.map` | `('a -> 'b) -> 'a list -> 'b list` |
| `List.rev_map` | `('a -> 'b) -> 'a list -> 'b list` |
| `List.mapi` | `(int -> 'a -> 'b) -> 'a list -> 'b list` |
| `List.iter` | `('a -> unit) -> 'a list -> unit` |
| `List.iteri` | `(int -> 'a -> unit) -> 'a list -> unit` |
| `List.fold_left` | `('a -> 'b -> 'a) -> 'a -> 'b list -> 'a` |
| `List.fold_right` | `('a -> 'b -> 'b) -> 'a list -> 'b -> 'b` |
| `List.filter` | `('a -> bool) -> 'a list -> 'a list` |
| `List.exists` | `('a -> bool) -> 'a list -> bool` |
| `List.find` | `('a -> bool) -> 'a list -> 'a` |
| `List.filter_map` | `('a -> 'b option) -> 'a list -> 'b list` |
| `List.for_all` | `('a -> bool) -> 'a list -> bool` |
| `List.mem` | `'a -> 'a list -> bool` |
| `List.assoc` | `'a -> ('a * 'b) list -> 'b` |
| `List.split` | `('a * 'b) list -> 'a list * 'b list` |
| `List.combine` | `'a list -> 'b list -> ('a * 'b) list` |
| `List.sort` | `('a -> 'a -> int) -> 'a list -> 'a list` |
| `List.init` | `int -> (int -> 'a) -> 'a list` |

### Array

| name | type |
| --- | --- |
| `Array.length` | `'a array -> int` |
| `Array.make` | `int -> 'a -> 'a array` |
| `Array.init` | `int -> (int -> 'a) -> 'a array` |
| `Array.make_matrix` | `int -> int -> 'a -> 'a array array` |
| `Array.get` | `'a array -> int -> 'a` |
| `Array.set` | `'a array -> int -> 'a -> unit` |
| `Array.copy` | `'a array -> 'a array` |
| `Array.sub` | `'a array -> int -> int -> 'a array` |
| `Array.append` | `'a array -> 'a array -> 'a array` |
| `Array.of_list` | `'a list -> 'a array` |
| `Array.to_list` | `'a array -> 'a list` |
| `Array.iter` | `('a -> unit) -> 'a array -> unit` |
| `Array.iteri` | `(int -> 'a -> unit) -> 'a array -> unit` |
| `Array.map` | `('a -> 'b) -> 'a array -> 'b array` |
| `Array.fold_left` | `('a -> 'b -> 'a) -> 'a -> 'b array -> 'a` |
| `Array.sort` | `('a -> 'a -> int) -> 'a array -> unit` |
| `Array.blit` | `'a array -> int -> 'a array -> int -> int -> unit` |
| `Array.fill` | `'a array -> int -> int -> 'a -> unit` |

### String

| name | type |
| --- | --- |
| `String.length` | `string -> int` |
| `String.get` | `string -> int -> char` |
| `String.sub` | `string -> int -> int -> string` |
| `String.concat` | `string -> string list -> string` |
| `String.make` | `int -> char -> string` |
| `String.init` | `int -> (int -> char) -> string` |
| `String.index` | `string -> char -> int` |
| `String.contains` | `string -> char -> bool` |
| `String.uppercase_ascii` | `string -> string` |
| `String.lowercase_ascii` | `string -> string` |
| `String.split_on_char` | `char -> string -> string list` |
| `String.compare` | `string -> string -> int` |

### Char

| name | type |
| --- | --- |
| `Char.code` | `char -> int` |
| `Char.chr` | `int -> char` |
| `Char.escaped` | `char -> string` |
| `Char.lowercase_ascii` | `char -> char` |
| `Char.uppercase_ascii` | `char -> char` |

### Printf

| name | type |
| --- | --- |
| `Printf.printf` | `('a, out_channel, unit) format -> 'a` |
| `Printf.sprintf` | `('a, unit, string) format -> 'a` |

### Float

| name | type |
| --- | --- |
| `Float.pi` | `float` |
| `Float.exp` | `float -> float` |
| `Float.cos` | `float -> float` |
| `Float.sin` | `float -> float` |
| `Float.tan` | `float -> float` |

### Sys

| name | type |
| --- | --- |
| `Sys.argv` | `string array` |

### Random

| name | type |
| --- | --- |
| `Random.int` | `int -> int` |
| `Random.self_init` | `unit -> unit` |
| `Random.init` | `int -> unit` |

### Stack

| name | type |
| --- | --- |
| `Stack.create` | `unit -> 'a Stack.t` |
| `Stack.push` | `'a -> 'a Stack.t -> unit` |
| `Stack.pop` | `'a Stack.t -> 'a` |
| `Stack.top` | `'a Stack.t -> 'a` |
| `Stack.is_empty` | `'a Stack.t -> bool` |
| `Stack.length` | `'a Stack.t -> int` |

### Hashtbl

| name | type |
| --- | --- |
| `Hashtbl.create` | `int -> ('a, 'b) Hashtbl.t` |
| `Hashtbl.add` | `('a, 'b) Hashtbl.t -> 'a -> 'b -> unit` |
| `Hashtbl.replace` | `('a, 'b) Hashtbl.t -> 'a -> 'b -> unit` |
| `Hashtbl.remove` | `('a, 'b) Hashtbl.t -> 'a -> unit` |
| `Hashtbl.find` | `('a, 'b) Hashtbl.t -> 'a -> 'b` |
| `Hashtbl.find_opt` | `('a, 'b) Hashtbl.t -> 'a -> 'b option` |
| `Hashtbl.mem` | `('a, 'b) Hashtbl.t -> 'a -> bool` |
| `Hashtbl.length` | `('a, 'b) Hashtbl.t -> int` |


## Deliberate differences from OCaml

| | here | real OCaml |
| --- | --- | --- |
| `int` | unbounded | 63-bit, and it wraps |
| argument order | left to right | unspecified |
| `<` and friends | `int`, `float`, `char`, `string` | any type |
| tail calls | use stack | use none |
| `==` and `!=` | absent | physical equality |
| exhaustiveness of `match` | not checked | a warning |
| a string inside a comment | not scanned | scanned |
| `assert false` | of type `unit` | of any type |
| `Random` | Python's generator | OCaml's, so other numbers |

Each of those is a decision with a way out, which [the specification](specification.md#differences-from-ocaml) gives.

## Not in the subset

Modules, functors, objects, classes, GADTs, polymorphic variants, labelled and optional arguments, first-class modules, `lazy`, and user-defined operators.

`Printf`, `Hashtbl` and `Stack` are here, for the functions listed above. A `Printf` format is typed from its directives, `%d`, `%s`, `%f`, `%.2f`, `%c`, `%b` and their widths, as OCaml types it, and it has to be the literal string passed to `printf`: bound by `let` first, it is only a string.
