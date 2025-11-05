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
        self.acceptance_base = self.credence_endorsed_focal_subsets(2**self.concept_framework.n_props - 1)
        self.inferable_bases = self.get_inferable_base()

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
    
    def show_possibleworld_masses(self, as_table=False):
        """
        Display or return all propositions with their corresponding possible worlds and mass values.
        
        Parameters:
        - as_table (bool): if True, returns a list of dicts (for DataFrame use).
        
        Example:
            es.show_masses()              # prints mapping
            df = es.show_masses(True)     # returns list of dicts for DataFrame
        """
        rows = []
        for pid, mass in self.mass.items():
            worlds = self.concept_framework.get_proposition_worlds(pid)
            rows.append({
                "Proposition": f"P{pid}",
                "Worlds": ", ".join(worlds),
                "Mass": mass
            })
        
        if as_table:
            return rows
        
        for row in rows:
            print(f"{row['Proposition']} → [{row['Worlds']}] | mass = {row['Mass']}")

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


    def get_inferable_base(self,endorsed=True):
        """
        Efficient search for maximal consistent subsets among focal subsets of the full proposition (2**n - 1).

        Algorithm:
        - Start from the full set of focal propositions.
        - If its intersection of worlds is non-empty -> it's the unique maximal set.
        - Else recursively remove propositions one by one.
        - Keep subsets whose intersection is non-empty and cannot be further extended without becoming inconsistent.
        """
        full_prop_id = 2**self.concept_framework.n_props - 1
        if (endorsed):
            focal = self.endorsed_focal_subsets(full_prop_id)
            print(focal)
        else:
            focal = self.focal_subsets(full_prop_id)
            print(focal)

        prop_worlds = {pid: set(self.concept_framework.get_proposition_worlds(pid)) for pid in focal}

        results = []

        def intersection_of(subset):
            """Compute intersection of worlds for a subset of proposition ids."""
            if not subset:
                return set()
            inter = set(prop_worlds[next(iter(subset))])
            for pid in subset:
                inter &= prop_worlds[pid]
                if not inter:
                    break
            return inter

        def search(current_subset):
            inter = intersection_of(current_subset)
            if not inter:
                return False  # inconsistent

            # Try to add back any missing focal element to test maximality
            extended = False
            for pid in focal:
                if pid not in current_subset:
                    new_subset = current_subset | {pid}
                    if intersection_of(new_subset):
                        # It can be extended; keep searching for a larger consistent set
                        extended = True
                        search(new_subset)

            # If cannot extend further, this subset is maximal
            if not extended:
                if current_subset not in results:
                    results.append(current_subset)
            return True

        # Start from the full set; if inconsistent, recursively prune
        def prune(subset):
            inter = intersection_of(subset)
            if inter:
                # If consistent, check if it's maximal
                search(subset)
            else:
                # Remove one proposition at a time and explore
                for pid in subset:
                    smaller = subset - {pid}
                    if smaller and smaller not in results:
                        prune(smaller)

        prune(set(focal))

        # Deduplicate by sorted tuple
        unique_results = []
        seen = set()
        for s in results:
            t = tuple(sorted(s))
            if t not in seen:
                seen.add(t)
                unique_results.append(s)

        # Return list of (subset, intersection_of_worlds)
        return [(s, intersection_of(s)) for s in unique_results]

    def get_grounds(self, target_prop_id):
        """
        For a given proposition, find grounds across all inferable bases.

        A ground for a proposition X is one of the smallest subsets of an inferable base
        whose intersection is non-empty and contained within X, such that removing any
        proposition breaks this property.

        Returns:
            List of tuples: (inferable_base, ground, min_mass)
        """
        target_worlds = set(self.concept_framework.get_proposition_worlds(target_prop_id))
        results = []

        # Iterate over each inferable base
        for base, base_intersection in self.inferable_bases:
            base_props = list(base)
            prop_worlds = {pid: set(self.concept_framework.get_proposition_worlds(pid)) for pid in base_props}

            def intersection_of(subset):
                """Compute intersection of worlds for a subset of proposition IDs."""
                if not subset:
                    return set()
                inter = set(prop_worlds[next(iter(subset))])
                for pid in subset:
                    inter &= prop_worlds[pid]
                    if not inter:
                        break
                return inter

            def min_mass(subset):
                """Get the minimum mass among propositions in subset."""
                masses = [self.mass.get(pid, 0) for pid in subset]
                return min(masses) if masses else 0

            grounds_for_base = []

            # Recursive search for minimal subsets
            def search(current_set, remaining_props):
                if current_set:
                    inter = intersection_of(current_set)
                else:
                    inter = target_worlds.copy()

                # Skip empty or irrelevant intersections
                if not inter or not inter.issubset(target_worlds):
                    return

                # Check minimality
                for g in grounds_for_base:
                    if g.issubset(current_set):
                        return

                if current_set:
                    grounds_for_base.append(set(current_set))

                for i, pid in enumerate(remaining_props):
                    search(current_set | {pid}, remaining_props[i+1:])

            search(set(), base_props)

            # Add results with min mass
            for g in grounds_for_base:
                results.append((set(base_props), g, min_mass(g)))

        return results
    
    
    def get_strongest_grounds(self, target_prop_id):
        """
        Determine the strongest grounds for a target proposition.

        Uses get_grounds() and returns:
        - strongest grounds within each inferable base
        - globally strongest grounds across all bases
        """
        all_grounds = self.get_grounds(target_prop_id)
        if not all_grounds:
            return {"by_base": [], "global": []}

        # --- Group by inferable base ---
        from collections import defaultdict
        base_groups = defaultdict(list)
        for base, ground, strength in all_grounds:
            base_groups[frozenset(base)].append((ground, strength))

        # --- Find strongest per base ---
        by_base = []
        for base, grounds in base_groups.items():
            max_strength = max(strength for _, strength in grounds)
            strongest_in_base = [
                (set(base), g, s) for g, s in grounds if s == max_strength
            ]
            by_base.extend(strongest_in_base)

        # --- Find globally strongest ---
        global_max = max(s for _, _, s in by_base)
        global_strongest = [
            (base, g, s) for base, g, s in by_base if s == global_max
        ]

        return {
            "by_base": by_base,
            "global": global_strongest
        }
