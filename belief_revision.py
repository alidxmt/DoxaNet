from typing import List
import json
from epistemic_space import EpistemicSpace  # import from the same folder

class BeliefRevision:
    def __init__(self, name: str, propositions=None, beliefs=None,
                 core=None, entrenchment=None):
        self.name = name
        self.propositions = propositions or []  # list of proposition names
        self.K = beliefs or []                  # current belief set
        self.core = set(core or [])             # core beliefs (cannot remove)
        self.entrenchment = entrenchment or {}  # numeric ranks
        
        # Initialize epistemic space
        self.space = EpistemicSpace(len(self.propositions), self.propositions)
        self.possibilities = set(range(self.space.n_possibilities))
        self.core_worlds = self._compute_core_worlds()

    # ----------------------
    # JSON persistence
    # ----------------------
    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf8") as f:
            data = json.load(f)
        return cls(
            name=data["meta"]["name"],
            propositions=data["meta"]["propositions"],
            beliefs=data["beliefs"]["K"],
            core=data["beliefs"].get("core", []),
            entrenchment=data.get("entrenchment", {})
        )

    def to_json(self, path: str):
        data = {
            "meta": {"name": self.name, "propositions": self.propositions},
            "beliefs": {"K": self.K, "core": list(self.core)},
            "entrenchment": self.entrenchment
        }
        with open(path, "w", encoding="utf8") as f:
            json.dump(data, f, indent=2)

    # ----------------------
    # Utility methods
    # ----------------------
    def rank(self, sentence: str) -> int:
        return self.entrenchment.get(sentence, 0)

    def is_core(self, sentence: str) -> bool:
        return sentence in self.core

    def _compute_core_worlds(self):
        worlds = set(range(self.space.n_possibilities))
        for prop in self.core:
            idx = self.propositions.index(prop)
            worlds = {w for w in worlds if self.space.get_possibility_bitstring(w)[idx] == "1"}
        return worlds

    # ----------------------
    # Belief revision operations
    # ----------------------
    def contract(self, sentence_to_remove: str):
        rank_p = self.rank(sentence_to_remove)
        new_K = [q for q in self.K if q != sentence_to_remove and (self.is_core(q) or self.rank(q) > rank_p)]
        removed = set(self.K) - set(new_K)
        self.K = new_K

        idx = self.propositions.index(sentence_to_remove)
        self.possibilities = {w for w in self.possibilities if self.space.get_possibility_bitstring(w)[idx] == "0"}
        if not self.possibilities:
            print("Warning: contraction leads to empty epistemic state!")
        return removed

    def expand(self, sentence: str):
        if sentence not in self.K:
            self.K.append(sentence)
        idx = self.propositions.index(sentence)
        self.possibilities = {w for w in self.possibilities if self.space.get_possibility_bitstring(w)[idx] == "1"}
        if not self.possibilities:
            print("Warning: expansion leads to empty epistemic state!")

    def reset(self, beliefs: List[str] = None):
        self.K = beliefs.copy() if beliefs else []

    # ----------------------
    # Dynamic updates
    # ----------------------
    def add_proposition(self, prop: str, is_core=False, rank: int = 0):
        if prop not in self.propositions:
            self.propositions.append(prop)
            self.space = EpistemicSpace(len(self.propositions), self.propositions)
            self.possibilities = set(range(self.space.n_possibilities))
        if prop not in self.K:
            self.K.append(prop)
        if is_core:
            self.core.add(prop)
        self.entrenchment[prop] = rank
        self.core_worlds = self._compute_core_worlds()

    def set_core(self, prop: str, value: bool = True):
        if value:
            self.core.add(prop)
        else:
            self.core.discard(prop)
        self.core_worlds = self._compute_core_worlds()

    def set_entrenchment(self, prop: str, rank: int):
        self.entrenchment[prop] = rank

    def remove_proposition(self, prop: str):
        if prop in self.core:
            raise ValueError(f"Cannot remove core belief '{prop}'")
        self.K = [b for b in self.K if b != prop]
        if prop in self.propositions:
            self.propositions.remove(prop)
        self.entrenchment.pop(prop, None)
        self.space = EpistemicSpace(len(self.propositions), self.propositions)
        self.possibilities = set(range(self.space.n_possibilities))
        self.core_worlds = self._compute_core_worlds()
