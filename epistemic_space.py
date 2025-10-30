import itertools

# Epistemic Space is general class for various theories in formal epistemology. 
class EpistemicSpace:
    def __init__(self, conceptual_framework, mass):
        self.concept_framework = conceptual_framework
        self.mass_thresholds = {}          # proposition P-decimal → mass threshold
        self.global_mass_threshold = 0 # mass threshold for all except in mass threshold
        self.credence_thresholds = {} # proposition P-decimal → credence threshold
        self.credence_global_threshold = 0 ## credence threshold for all except in credence threshold
        self.mass = mass                   # proposition P-decimal → mass more than 0 to 1 / (0,1)

    def set_mass(self, prop_id, value):
        """
        Assign a mass (0-1) to a proposition P_prop_id.
        """
        if not (0 <= value <= 1):
            raise ValueError("Mass must be between 0 and 1")
        self.mass[prop_id] = value

    def get_mass(self, prop_id):
        """
        Retrieve the mass assigned to proposition P_prop_id.
        Returns 0 if no mass assigned.
        """
        return self.mass.get(prop_id, 0)

    def get_mass_threshold(self, prop_id):
        """
        Return the mass threshold for a proposition.
        Uses specific mass threshold if set, otherwise global mass threshold.
        """
        return self.mass_thresholds.get(prop_id, self.global_mass_threshold)
    
    def get_credence_threshold(self, prop_id):
        """
        Return the credence threshold for a proposition.
        Uses specific credence threshold if set, otherwise global credence threshold.
        """
        return self.credence_thresholds.get(prop_id, self.credence_global_threshold)

    def focal_subsets(self, prop_id):
        """
        Return all propositions (keys in self.mass) that are subsets of the 
        given proposition P_prop_id. Only considers propositions that have mass assigned.
        """
        target_worlds = set(self.concept_framework.get_proposition_worlds(prop_id))
        
        focal_subsets = []
        for pid in self.mass:
            prop_worlds = set(self.concept_framework.get_proposition_worlds(pid))
            if prop_worlds and prop_worlds.issubset(target_worlds):
                focal_subsets.append(pid)
        
        return focal_subsets

    def endorsed_focal_subsets(self, prop_id):
        """
        Return all focal subsets of P_prop_id that meet their mass threshold,
        or the global mass threshold if no specific threshold is set.
        """
        target_worlds = set(self.concept_framework.get_proposition_worlds(prop_id))
        
        endorsed_subsets = []
        for pid in self.mass:
            prop_worlds = set(self.concept_framework.get_proposition_worlds(pid))
            if not prop_worlds.issubset(target_worlds):
                continue  # only subsets
            if self.mass.get(pid, 0) >= self.get_mass_threshold(pid):
                endorsed_subsets.append(pid)
        
        return endorsed_subsets
    
    def credence_focal_subsets(self, prop_id):
        """
        Calculate the credence of a proposition as the sum of masses
        of all its focal subsets.
        """
        total_credence = 0
        for pid in self.focal_subsets(prop_id):
            total_credence += self.get_mass(pid)
        return total_credence


    def credence_endorsed_focal_subsets(self, prop_id):
        """
        Calculate the credence of a proposition as the sum of masses
        of all its endorsed focal subsets (meeting mass thresholds).
        """
        total_credence = 0
        for pid in self.endorsed_focal_subsets(prop_id):
            total_credence += self.get_mass(pid)
        return total_credence

    def ground_sets(self, prop_id):
        """
        Return all minimal ground sets of focal propositions for prop_id.
        Each ground set is a set of focal subsets whose intersection is
        contained in prop_id, and minimal in the sense that removing any
        member breaks this property.
        """
        # Step 1: focal subsets (only those with mass)
        focal = self.focal_subsets(prop_id)
        ground_sets_list = []

        # Step 2: generate all non-empty combinations
        for r in range(1, len(focal)+1):
            for combo in itertools.combinations(focal, r):
                # Compute intersection of worlds
                combo_worlds = [set(self.concept_framework.get_proposition_worlds(pid)) for pid in combo]
                intersection = set.intersection(*combo_worlds)
                target_worlds = set(self.concept_framework.get_proposition_worlds(prop_id))
                if intersection.issubset(target_worlds):
                    # Step 3: check minimality
                    minimal = True
                    for i in range(len(combo)):
                        reduced_combo = combo[:i] + combo[i+1:]
                        if reduced_combo:
                            reduced_intersection = set.intersection(*[set(self.concept_framework.get_proposition_worlds(pid)) for pid in reduced_combo])
                            if reduced_intersection.issubset(target_worlds):
                                minimal = False
                                break
                    if minimal:
                        ground_sets_list.append(set(combo))
        return ground_sets_list
    
    def min_mass_of_set(self, prop_ids):
        """
        For a set/list of propositions, return the minimum mass among them.
        Returns 'not assessable' if any proposition does not have mass assigned.
        """
        masses = []
        for pid in prop_ids:
            if pid not in self.mass:
                return "not assessable"
            masses.append(self.mass[pid])
        return min(masses) if masses else "not all propostions have mass"
    
    def ground_sets_with_min_mass(self, prop_id):
        """
        For a given proposition, return a list of tuples:
        (ground_set, minimum mass of that set)
        If any proposition in a ground set lacks mass, min mass is 'not assessable'.
        """
        result = []
        ground_sets_list = self.ground_sets(prop_id)
        
        for gset in ground_sets_list:
            min_mass = self.min_mass_of_set(gset)
            result.append((gset, min_mass))
        
        return result

    def inferable_sets(self):
        """
        Compute all maximal consistent inferable sets from the acceptance base
        (endorsed focal subsets). A set of propositions is inferable if the 
        intersection of all its worlds is non-empty, and maximal.
        """
        X = self.endorsed_focal_subsets_for_all()  # assume returns list/set of proposition IDs
        if not X:
            return []

        # Step 1: map each proposition to its world set
        prop_worlds = {pid: set(self.concept_framework.get_proposition_worlds(pid)) for pid in X}

        # Step 2: initialize candidate sets with singletons
        candidates = [{pid} for pid in X]

        # Step 3: iteratively merge candidates
        changed = True
        while changed:
            changed = False
            new_candidates = []
            used = set()
            for i, c1 in enumerate(candidates):
                if i in used:
                    continue
                merged = c1.copy()
                for j, c2 in enumerate(candidates):
                    if j <= i or j in used:
                        continue
                    # compute intersection of worlds
                    intersection = set.intersection(*(prop_worlds[pid] for pid in merged | c2))
                    if intersection:  # consistent
                        merged |= c2
                        used.add(j)
                        changed = True
                new_candidates.append(merged)
            candidates = new_candidates

        # Step 4: remove duplicates (sets may have merged into same)
        unique_candidates = []
        seen = []
        for s in candidates:
            if s not in seen:
                unique_candidates.append(s)
                seen.append(s)

        return unique_candidates
