# Aide-mémoire

Cette page rassemble tout ce que contient le sous-ensemble.

!!! note "Trois de ces tableaux sont engendrés"
    Les opérateurs, les mots-clés et la bibliothèque standard sont lus
    directement dans le compilateur au moment où cette page est construite :
    ils ne peuvent donc pas prendre du retard sur lui. Le texte autour est
    écrit à la main.

## Définitions

```ocaml
let x = 42
let f x y = x + y                     (* deux paramètres *)
let rec fact n =                      (* rec, pour un appel récursif *)
  if n <= 1 then 1 else n * fact (n - 1)
let rec pair n = ... and impair n = ...  (* récursivité croisée *)
let () = print_int (fact 5)           (* exécuter quelque chose *)
let a, b = 1, 2                       (* un motif lie *)
let g x = let y = x * 2 in y + 1      (* local, avec `in` *)
```

## Types

```ocaml
int  float  char  string  bool  unit  exn
'a list        'a array       'a option      'a ref
int * string                          (* un couple *)
int -> int -> int                     (* une fonction à deux arguments *)

type couleur = Rouge | Vert | Bleu
type 'a arbre = Vide | Noeud of 'a arbre * 'a * 'a arbre
type point = { x : float; mutable y : float }
type entier = int                     (* un alias *)
exception Vide
exception Trop_grand of int
```

Un constructeur prend un argument, et `of int * string` fait de cet argument un couple. `mutable` est ce qui permet d'affecter un champ avec `<-`.

## Expressions

```ocaml
if c then a else b                    (* les deux branches, même type *)
match e with | p -> a | q when g -> b
function | p -> a | q -> b            (* une fonction qui filtre *)
fun x y -> e                          (* anonyme *)
try e with Vide -> a | Failure m -> b
while c do e done
for i = 0 to n - 1 do e done          (* `downto` décompte *)
a; b                                  (* a est évalué pour son effet *)
begin a; b end                        (* pareil, entre délimiteurs *)
[ 1; 2; 3 ]      1 :: reste      l1 @ l2
[| 1; 2; 3 |]    t.(i)           t.(i) <- v
s.[i]            "bon" ^ "jour"
{ x = 1.0; y = 2.0 }    p.x      p.y <- 3.0    { p with x = 0.0 }
let r = ref 0 in r := !r + 1; incr r
```

## Motifs

```ocaml
_                    x                    42        'a'       "s"
(a, b)               a :: reste           []        [ a; b ]  [| a; b |]
Noeud (g, v, d)      Some x               None
{ x = a; y = b }     p as tout            0 | 1 | 2
```

Toutes les alternatives d'un motif `|` doivent lier les mêmes noms. Un cas peut porter une garde : `| n when n < 0 -> ...`.

## Opérateurs

Les opérateurs vont du plus prioritaire au moins prioritaire. L'application est plus prioritaire que tous, et les préfixes `-`, `-.` et `!` davantage encore.

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

Les formes avec un point sont pour les flottants : `1 + 2` et `1.0 +. 2.0`, jamais les deux mélangés. `=` est l'égalité structurelle, `<>` sa négation, et `:=` écrit à travers une `ref`. N'importe lequel s'utilise comme valeur en le mettant entre parenthèses, comme dans `List.fold_left ( + ) 0`.

## Mots-clés

`and` `as` `asr` `begin` `do` `done` `downto` `else` `end` `exception` `false` `for` `fun` `function` `if` `in` `land` `let` `lor` `lsl` `lsr` `lxor` `match` `mod` `mutable` `of` `rec` `then` `to` `true` `try` `type` `when` `while` `with`

## La bibliothèque standard

Voici tout ce qu'un programme peut utiliser sans le définir, avec son type. Il n'y a pas d'`open` : un nom de module est un préfixe.

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


## Différences volontaires avec OCaml

| | ici | le vrai OCaml |
| --- | --- | --- |
| `int` | non borné | 63 bits, et il boucle |
| ordre des arguments | de gauche à droite | non spécifié |
| `<` et ses semblables | `int`, `float`, `char`, `string` | n'importe quel type |
| appels terminaux | consomment de la pile | n'en consomment pas |
| `==` et `!=` | absents | égalité physique |
| exhaustivité d'un `match` | non vérifiée | un avertissement |
| une chaîne dans un commentaire | non analysée | analysée |
| `assert false` | de type `unit` | de n'importe quel type |
| `Random` | le générateur de Python | celui d'OCaml, donc d'autres nombres |

Chacune est une décision assumée, avec une porte de sortie, que donne la [spécification](specification.md#differences-avec-ocaml).

## Hors du sous-ensemble

Le sous-ensemble n'a ni modules, ni foncteurs, ni objets, ni classes, ni GADT, ni variants polymorphes, ni arguments étiquetés ou optionnels, ni modules de première classe, ni `lazy`, ni opérateurs définis par l'utilisateur.

`Printf`, `Hashtbl` et `Stack` sont là, pour les fonctions listées plus haut. Comme en OCaml, un format de `Printf` est typé d'après ses directives : `%d`, `%s`, `%f`, `%.2f`, `%c`, `%b` et leurs largeurs. Il doit être la chaîne littérale passée à `printf` ; liée d'abord par un `let`, ce n'est plus qu'une chaîne.
