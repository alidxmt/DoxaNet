import math
import json
import re
import builtins

class ConceptualFramework:
    def __init__(self, n_props, sentences=None,global_shortcuts=False):
        self.n_props = n_props
        self.n_worlds = 2 ** n_props
        self.n_propositions = 2 ** self.n_worlds

        # Conceptual framework (basic sentences)
        self.conceptual_framework = [f"B{i+1}" for i in range(n_props)]

        # Optional user-defined sentence strings
        if sentences is None:
            sentences = [f"Sentence {i+1}" for i in range(n_props)]
        if len(sentences) != n_props:
            raise ValueError("Length of sentences must match n_props")

        self.sentences = {self.conceptual_framework[i]: sentences[i] for i in range(n_props)}

        # Build worlds and propositions
        self.possible_worlds = self._build_worlds()
        self.possibilities = [w["label"] for w in self.possible_worlds]
        if n_props <= 3:
                    self.propositions = self._build_propositions()
        else:
            self.propositions = f"{self.n_propositions} possible propositions (2**(2**{n_props})) too many to calculate"
            
        # Add functions for notebook convenience
        self.w = lambda i: self._world_view(i)
        self.p = lambda k: self._prop_view(k)
        
        # Optional global shortcuts
        if global_shortcuts:
            builtins.W = self.w
            builtins.P = self.p
            builtins.g = self.g
            builtins.prt = self.prt
    
    # -----------------------------------------------------
    # --- LOGICAL EXPRESSION PARSER FOR PROPOSITIONS ---
    # -----------------------------------------------------
    def prt(self, expr):
        """
        Pretty-print worlds, propositions, or g() results:
        - If expr is dict from g(), pretty both 'worlds' and 'notation'
        - If expr is string or list of strings, convert Pn/Wn to subscript
        """
        sub_map = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

        def repl(m):
            label = m.group()
            match = re.match(r'([WPwp])(\d+)', label)
            if not match:
                return label
            base, num = match.groups()
            return base.upper() + num.translate(sub_map)

        if isinstance(expr, dict) and "worlds" in expr and "notation" in expr:
            return {
                "worlds": [re.sub(r'[WPwp]\d+', repl, w) for w in expr["worlds"]],
                "notation": re.sub(r'[WPwp]\d+', repl, expr["notation"])
            }
        elif isinstance(expr, list):
            return [re.sub(r'[WPwp]\d+', repl, e) for e in expr]
        elif isinstance(expr, str):
            return re.sub(r'[WPwp]\d+', repl, expr)
        else:
            raise TypeError("Input must be string, list of strings, or g() result dict")


    # -----------------------------------------------------
    # --- RETURN SINGLETON PROPOSITIONS ---
    # -----------------------------------------------------
    def get_singletons(self):
        """Return a list of propositions corresponding to single-world sets (atomic propositions)."""
        return [self._prop_view(2**i) for i in range(self.n_worlds)]

    # -----------------------------------------------------
    # --- LOGICAL EXPRESSION PARSER FOR PROPOSITIONS ---
    # -----------------------------------------------------
    def g(self, expr_str):
        """
        Evaluate a logical expression like '(P3 & P5) || (P1)'.
        Returns:
        - 'worlds': list of world labels where expression is True
        - 'notation': compact set-theoretic notation '(P3∩P5)∪(P1)'
        """
        # Normalize keyboard symbols
        expr = expr_str.replace("&&", " and ").replace("&", " and ")
        expr = expr.replace("||", " or ").replace("|", " or ")
        expr = expr.replace("!", " not ")

        # Build clean set-theoretic notation
        notation = expr
        notation = re.sub(r"\band\b", "∩", notation)
        notation = re.sub(r"\bor\b", "∪", notation)
        notation = re.sub(r"\s+", "", notation)  # remove all spaces
        notation = notation.strip()

        # Find all proposition tokens
        prop_tokens = re.findall(r"P\d+", expr)

        satisfying_worlds = []

        for w in self.possible_worlds:
            # Map each proposition to True/False for this world
            local_dict = {t: w["label"] in self.get_proposition_worlds(int(t[1:])) 
                        for t in prop_tokens}

            # Evaluate expression for this world
            try:
                if eval(expr, {}, local_dict):
                    satisfying_worlds.append(w["label"])
            except Exception as e:
                raise ValueError(f"Cannot evaluate expression: {expr_str}. Error: {e}")

        return {"worlds": satisfying_worlds, "notation": notation}


    # -----------------------------------------------------
    # --- WORLD VIEW METHOD ---
    # -----------------------------------------------------
    def _world_view(self, i):
        """Return an object-like view for a world."""
        w = self.possible_worlds[i]
        class WorldView:
            def __init__(self, world):
                self.id = world["id"]
                self.label = world["label"]
                self.bitstring = world["bitstring"]
                self.notation = world["notation"]
                self.sentence = world["sentence_form"]
            def __repr__(self):
                return f"<{self.label}: bitstring={self.bitstring}, notation={self.notation}>"
        return WorldView(w)

    # -----------------------------------------------------
    # --- PROPOSITION VIEW METHOD ---
    # -----------------------------------------------------
    
    def _prop_view(self, k):
        """Return an object-like view for a proposition."""
        class PropView:
            def __init__(self, space, prop_id):
                self.space = space
                self.id = prop_id
                self.label = f"P{prop_id}"

            @property
            def worlds(self):
                # Safe: return empty list for huge indices
                return self.space.get_proposition_worlds(self.id)

            @property
            def bitstring(self):
                if 0 <= self.id < self.space.n_propositions and self.space.n_props <= 3:
                    return self.space.get_proposition_bitstring(self.id)
                # Return empty or placeholder for huge indices
                return ""

            @property
            def notation(self):
                return " ∪ ".join(self.worlds) if self.worlds else "does not exist"

            def __repr__(self):
                if self.worlds:
                    return f"<{self.label}: worlds={self.worlds}, bitstring={self.bitstring}>"
                else:
                    return f"<{self.label}: does not exist, max index={self.space.n_propositions - 1}>"

        return PropView(self, k)

    # -----------------------------------------------------
    # --- WORLD CONSTRUCTION METHODS ---
    # -----------------------------------------------------
    def get_world_bitstring(self, i):
        """Return the binary truth vector of world i."""
        return format(i, f'0{self.n_props}b')

    def get_world_notation(self, i):
        """Return set-theoretic notation of world i."""
        bits = self.get_world_bitstring(i)
        terms = []
        for j, bit in enumerate(bits):
            prop = self.conceptual_framework[j]
            terms.append(prop if bit == "1" else f"¬{prop}")
        return " ∩ ".join(terms)

    def _build_worlds(self):
        """Construct all possible worlds with binary and semantic representation."""
        worlds = []
        for i in range(self.n_worlds):
            bitstring = self.get_world_bitstring(i)
            notation = self.get_world_notation(i)
            sentence_form = self.get_sentence_notation(i)
            worlds.append({
                "id": i,
                "label": f"W{i}",
                "bitstring": bitstring,
                "notation": notation,
                "sentence_form": sentence_form
            })
        return worlds

    def get_sentence_notation(self, i):
        """Return full sentential version with negations and parentheses."""
        bits = self.get_world_bitstring(i)
        terms = []
        for j, bit in enumerate(bits):
            s = self.sentences[self.conceptual_framework[j]]
            term = s if bit == "1" else f"not the case that {s}"
            terms.append(f"({term})")
        return " ∩ ".join(terms)

    # -----------------------------------------------------
    # --- PROPOSITION CONSTRUCTION METHODS ---
    # -----------------------------------------------------
    def get_proposition_bitstring(self, k):
        """Return the binary membership vector of proposition k over worlds."""
        return format(k, f'0{self.n_worlds}b')

    def get_proposition_worlds(self, k):
        """Return the set of worlds where proposition P_k holds."""
        if not (0 <= k < self.n_propositions):
            # For huge or out-of-range indices, return empty list
            return []
        
        bitstring = self.get_proposition_bitstring(k)
        worlds = [f"W{i}" for i, bit in enumerate(bitstring[::-1]) if bit == "1"]
        return worlds



    def _build_propositions(self):
        """Construct all propositions as sets of worlds."""
        props = []
        for k in range(self.n_propositions):
            bitstring = self.get_proposition_bitstring(k)
            worlds = self.get_proposition_worlds(k)
            props.append({
                "id": k,
                "label": f"P{k}",
                "bitstring": bitstring,
                "worlds": worlds
            })
        return props

    # -----------------------------------------------------
    # --- EVALUATION UTILITIES ---
    # -----------------------------------------------------
    def worlds_satisfying(self, formula_fn):
        """Return list of worlds where formula_fn(bitstring) is True."""
        valid = []
        for w in self.possible_worlds:
            if formula_fn(w["bitstring"]):
                valid.append(w["label"])
        return valid

    def worlds_satisfying_expr(self, expr_str):
        """
        Evaluate expression of form '(B1 ∩ ¬B2) ∪ B3' and return worlds satisfying it.
        Uses binary world evaluation.
        """
        try:
            expr_no_space = expr_str.replace(" ", "")
            token_pattern = r"¬?B\d+|[∩∪\(\)]"
            tokens = re.findall(token_pattern, expr_no_space)
            if "".join(tokens) != expr_no_space:
                return "not well-formed: invalid character or token"

            # Check parentheses
            stack = []
            for t in tokens:
                if t == "(":
                    stack.append("(")
                elif t == ")":
                    if not stack:
                        return "not well-formed: unmatched closing parenthesis"
                    stack.pop()
            if stack:
                return "not well-formed: unmatched opening parenthesis"

            # Translate ∩, ∪ into Python and/or
            expr = expr_str.replace("∩", " and ").replace("∪", " or ")

            result = {"worlds": [], "worldsbit": [], "worldsnotation": []}
            for w in self.possible_worlds:
                bits = w["bitstring"]
                eval_expr = expr
                for i, prop in enumerate(self.conceptual_framework):
                    eval_expr = eval_expr.replace(f"¬{prop}", f"bits[{i}]=='0'")
                    eval_expr = eval_expr.replace(f"{prop}", f"bits[{i}]=='1'")
                if eval(eval_expr):
                    result["worlds"].append(w["label"])
                    result["worldsbit"].append(bits)
                    result["worldsnotation"].append(w["notation"])
            return result

        except SyntaxError:
            return "not well-formed: syntax error"
        except Exception:
            return "not well-formed: unknown error"

    # -----------------------------------------------------
    # --- DISPLAY UTILITIES ---
    # -----------------------------------------------------
    def show_worlds(self, limit=16):
        """Display worlds up to given limit."""
        return self.possible_worlds[:limit]

    def show_propositions(self, limit=16):
        """Display propositions up to given limit, computed on demand."""
        props = []
        for k in range(limit):
            props.append(self._prop_view(k))
        return props


    def to_json(self, limit_worlds=8, limit_props=8):
        """Export a compact JSON-style representation for inspection."""
        data = {
            "n_props": self.n_props,
            "worlds": self.show_worlds(limit_worlds),
            "propositions": self.show_propositions(limit_props)
        }
        return json.dumps(data, indent=2)


    # -----------------------------------------------------
    # --- PROPOSITIONAL VIEW ---
    # -----------------------------------------------------
    def _prop_view(self, k):
        """Return an object-like view for a proposition, computed on demand."""
        max_p = 2**(2**self.n_props)-1
        if not (0 <= k < self.n_propositions):
            # Graceful fallback for invalid proposition
            class InvalidProp:
                def __init__(self, k, max_p):
                    self.id = k
                    self.label = f"P{k} (does not exist)"
                    self.worlds = []
                    self.bitstring = ""
                def __repr__(self):
                    return f"<{self.label}: does not exist, max index={max_p}>"
            return InvalidProp(k, self.n_propositions - 1)

        class PropView:
            def __init__(self, space, prop_id):
                self.space = space
                self.id = prop_id
                self.label = f"P{prop_id}"

            @property
            def worlds(self):
                return self.space.get_proposition_worlds(self.id)

            @property
            def bitstring(self):
                return self.space.get_proposition_bitstring(self.id)

            @property
            def notation(self):
                return " ∪ ".join(self.worlds)

            def __repr__(self):
                return f"<{self.label}: worlds={self.worlds}, bitstring={self.bitstring}>"

        return PropView(self, k)

    

    # -----------------------------------------------------
    # --- SPACE VISUALIZATION ---
    # -----------------------------------------------------
    def visu(self, max_worlds=None, max_props=None):
        """
        Display a text-based visualization of the epistemic space.
        Automatically limits large numbers of worlds/propositions.
        """
        # ----------------------------
        # Worlds Table
        # ----------------------------
        print("="*80)
        print("WORLD TABLE".center(80))
        print("="*80)
        print(f"{'Label':<6} | {'Bitstring':<8} | {'Notation':<20} | {'Sentence'}")
        print("-"*80)
        
        # Determine which worlds to display
        if self.n_worlds <= 16:
            worlds_to_show = self.possible_worlds
        else:
            # first 8 and last 8
            worlds_to_show = self.possible_worlds[:8] + [{"label": "...", "bitstring": "...", "notation": "...", "sentence_form": "..."}] + self.possible_worlds[-8:]
        
        for w in worlds_to_show:
            print(f"{w['label']:<6} | {w['bitstring']:<8} | {w['notation']:<20} | {w['sentence_form']}")
        print("="*80)
        print()

        # ----------------------------
        # Propositions Table
        # ----------------------------
        print("="*80)
        print("PROPOSITION TABLE".center(80))
        print("="*80)
        print(f"{'Label':<6} | {'Bitstring':<12} | {'Worlds'}")
        print("-"*80)
        
        # Determine how many propositions to compute
        if self.n_props <= 3:
            total_props = self.n_propositions
        else:
            total_props = min(max_props or 16, self.n_propositions)
        
        for k in range(total_props):
            p = self._prop_view(k)
            worlds_str = ", ".join(p.worlds)
            print(f"{p.label:<6} | {p.bitstring:<12} | {worlds_str}")

        print("="*80)
