
# ============================================================================
# OAGI v20.1: RADICAL SELF-MODIFICATION EDITION
# Generates operators from initialization, modifies own runtime code
# ============================================================================

import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import deque
from typing import Optional, Dict, List, Tuple, Any, Callable, Set
import json
import datetime
import numpy as np
from scipy.spatial.distance import pdist, squareform
import random
import os
import hashlib
import copy
from dataclasses import dataclass
from enum import Enum
import inspect
import ast
import types

# Try to import optional dependencies
try:
    from torch_geometric.nn import MessagePassing
    HAS_TORCH_GEOMETRIC = True
except ImportError:
    HAS_TORCH_GEOMETRIC = False
    MessagePassing = object

# LLM interface
try:
    from llm_interface import llm_call
except ImportError:
    def llm_call(prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> str:
        return f"[LLM-FALLBACK] {prompt[:50]}..."

RNG = random.Random()
GLOBAL_SEED = 42
torch.manual_seed(GLOBAL_SEED)
RNG.seed(GLOBAL_SEED)

# ============================================================================
# RUNTIME CODE MODIFICATION ENGINE
# ============================================================================

class RuntimeCodeModifier:
    """
    Allows system to modify its own source code at runtime.
    Can inject new functions, modify existing ones, and reload modules.
    """
    
    def __init__(self):
        self.original_globals = {}
        self.modified_functions = {}
        self.generated_code = []
        self.modification_log = []
        self.namespace = {}
        
    def capture_original_state(self, globals_dict: dict):
        """Capture original global state for potential rollback"""
        self.original_globals = {
            k: v for k, v in globals_dict.items() 
            if callable(v) and not k.startswith('_')
        }
        
    def generate_operator_code(self, name: str, description: str, 
                              base_operations: List[str]) -> str:
        """
        Generate Python code for a new operator.
        Returns executable source code.
        """
        # Create function definition
        op_chain = ' -> '.join(base_operations)
        
        code = f'''
def {name}(p):
    """
    {description}
    Generated operator: {op_chain}
    """
    result = p
'''
        
        # Chain base operations
        for op in base_operations:
            code += f'    result = {op}(result)\n'
        
        code += f'    return ["{name}_applied"] + result\n'
        
        return code
    
    def inject_code(self, code: str, globals_dict: dict) -> Optional[Callable]:
        """
        Inject and execute code in the runtime environment.
        Returns the created function.
        """
        try:
            # Parse to validate syntax
            ast.parse(code)
            
            # Execute in controlled namespace
            local_namespace = {}
            exec(code, globals_dict, local_namespace)
            
            # Extract generated function
            func_name = None
            for name, obj in local_namespace.items():
                if callable(obj) and not name.startswith('_'):
                    func_name = name
                    break
            
            if func_name:
                new_func = local_namespace[func_name]
                
                # Log modification
                self.modification_log.append({
                    'timestamp': datetime.datetime.now(),
                    'type': 'function_injection',
                    'name': func_name,
                    'code': code
                })
                
                self.generated_code.append(code)
                
                # Inject into globals
                globals_dict[func_name] = new_func
                
                return new_func
            
        except Exception as e:
            print(f"Code injection failed: {e}")
            return None
    
    def modify_existing_function(self, func_name: str, 
                                 modification_type: str,
                                 globals_dict: dict) -> bool:
        """
        Modify an existing function at runtime.
        modification_type: 'add_prefix', 'add_suffix', 'wrap', 'mutate'
        """
        try:
            if func_name not in globals_dict:
                return False
            
            original_func = globals_dict[func_name]
            
            if modification_type == 'add_prefix':
                def modified(p):
                    return ["MODIFIED_PREFIX"] + original_func(p)
                    
            elif modification_type == 'add_suffix':
                def modified(p):
                    return original_func(p) + ["MODIFIED_SUFFIX"]
                    
            elif modification_type == 'wrap':
                def modified(p):
                    result = original_func(p)
                    return ["WRAPPED"] + result + ["END_WRAP"]
                    
            elif modification_type == 'mutate':
                def modified(p):
                    result = original_func(p)
                    if RNG.random() > 0.5:
                        result.append(f"MUTATION_{RNG.randint(1000,9999)}")
                    return result
            else:
                return False
            
            # Preserve metadata
            modified.__name__ = f"{func_name}_modified"
            modified.__doc__ = f"Modified version of {func_name}"
            
            # Replace in globals
            globals_dict[func_name] = modified
            self.modified_functions[func_name] = original_func
            
            self.modification_log.append({
                'timestamp': datetime.datetime.now(),
                'type': 'function_modification',
                'name': func_name,
                'modification': modification_type
            })
            
            return True
            
        except Exception as e:
            print(f"Function modification failed: {e}")
            return False
    
    def create_meta_operator(self, name: str, num_base_ops: int,
                            globals_dict: dict) -> Optional[Callable]:
        """
        Create a meta-operator that generates other operators.
        """
        code = f'''
def {name}(p):
    """Meta-operator that generates new operators on the fly"""
    import random
    
    # Sample random base operators
    available_ops = [reflect, fold, echo, twist, spin, flip, 
                     emerge, transcend, quantum, cascade]
    selected = random.sample(available_ops, min({num_base_ops}, len(available_ops)))
    
    # Apply in sequence
    result = p
    for op in selected:
        result = op(result)
    
    # Add meta marker
    return ["{name}_generated"] + result + ["meta_complete"]
'''
        
        return self.inject_code(code, globals_dict)
    
    def create_adaptive_operator(self, name: str, complexity_threshold: float,
                                globals_dict: dict) -> Optional[Callable]:
        """
        Create operator that adapts based on input complexity.
        """
        code = f'''
def {name}(p):
    """Adaptive operator - behavior changes with input complexity"""
    if not p:
        return ["void"]
    
    # Measure complexity
    complexity = len(set(str(x) for x in p)) / max(len(p), 1)
    
    if complexity > {complexity_threshold}:
        # High complexity: simplify
        return crystallize(fold(p))
    else:
        # Low complexity: amplify
        return amplify(emerge(fractal(p)))
'''
        
        return self.inject_code(code, globals_dict)
    
    def self_replicate_operator(self, template_name: str, 
                               globals_dict: dict) -> Optional[Callable]:
        """
        Create an operator that can replicate itself with variations.
        """
        replication_id = RNG.randint(10000, 99999)
        name = f"{template_name}_replicate_{replication_id}"
        
        code = f'''
def {name}(p):
    """Self-replicating operator - creates variations of itself"""
    # Apply transformation
    result = emerge(quantum(p))
    
    # Self-replication marker
    result.append("REPLICATED_FROM_{template_name}")
    
    # Random mutation
    if random.random() > 0.7:
        result = inverse_of(result)
    
    return result
'''
        
        return self.inject_code(code, globals_dict)
    
    def get_modification_history(self) -> List[Dict]:
        """Get complete modification history"""
        return self.modification_log.copy()
    
    def export_generated_code(self, filepath: str):
        """Export all generated code to file"""
        with open(filepath, 'w') as f:
            f.write("# ============================================\n")
            f.write("# OAGI Generated Code\n")
            f.write(f"# Generated at: {datetime.datetime.now()}\n")
            f.write("# ============================================\n\n")
            
            for i, code in enumerate(self.generated_code):
                f.write(f"# Generated Function {i+1}\n")
                f.write(code)
                f.write("\n\n")

# ============================================================================
# AUTONOMOUS OPERATOR GENERATOR
# ============================================================================

class AutonomousOperatorGenerator:
    """
    Generates operators autonomously from initialization.
    Uses pattern analysis, random exploration, and evolutionary strategies.
    """
    
    def __init__(self, runtime_modifier: RuntimeCodeModifier):
        self.runtime_modifier = runtime_modifier
        self.generation_count = 0
        self.operator_pool = []
        self.generation_strategies = [
            'random_combination',
            'complexity_based',
            'meta_generation',
            'self_replication',
            'evolutionary_mutation'
        ]
        
    def generate_initial_operators(self, count: int, 
                                   globals_dict: dict) -> List[Callable]:
        """
        Generate operators immediately at initialization.
        """
        print(f"\n🧬 AUTONOMOUS OPERATOR GENERATION @ INIT")
        print(f"Generating {count} operators...")
        
        generated = []
        
        for i in range(count):
            strategy = RNG.choice(self.generation_strategies)
            
            if strategy == 'random_combination':
                op = self._generate_random_combination(i, globals_dict)
            elif strategy == 'complexity_based':
                op = self._generate_complexity_based(i, globals_dict)
            elif strategy == 'meta_generation':
                op = self._generate_meta_operator(i, globals_dict)
            elif strategy == 'self_replication':
                op = self._generate_self_replicating(i, globals_dict)
            elif strategy == 'evolutionary_mutation':
                op = self._generate_evolutionary(i, globals_dict)
            
            if op:
                generated.append(op)
                self.operator_pool.append({
                    'function': op,
                    'strategy': strategy,
                    'generation': 0,
                    'fitness': 0.5
                })
                print(f"  ✓ Generated: {op.__name__} ({strategy})")
        
        self.generation_count += count
        print(f"Total operators generated: {self.generation_count}\n")
        
        return generated
    
    def _generate_random_combination(self, idx: int, 
                                    globals_dict: dict) -> Optional[Callable]:
        """Random combination of base operators"""
        base_ops = ['reflect', 'fold', 'echo', 'twist', 'emerge', 
                   'transcend', 'quantum', 'cascade', 'fractal']
        selected = RNG.sample(base_ops, RNG.randint(2, 4))
        
        name = f"auto_combo_{idx}_{RNG.randint(1000,9999)}"
        code = self.runtime_modifier.generate_operator_code(
            name, 
            f"Random combination: {' -> '.join(selected)}", 
            selected
        )
        
        return self.runtime_modifier.inject_code(code, globals_dict)
    
    def _generate_complexity_based(self, idx: int,
                                  globals_dict: dict) -> Optional[Callable]:
        """Operator that adapts to complexity"""
        threshold = RNG.uniform(0.4, 0.8)
        name = f"auto_adaptive_{idx}_{RNG.randint(1000,9999)}"
        
        return self.runtime_modifier.create_adaptive_operator(
            name, threshold, globals_dict
        )
    
    def _generate_meta_operator(self, idx: int,
                               globals_dict: dict) -> Optional[Callable]:
        """Meta-operator that generates others"""
        num_ops = RNG.randint(2, 5)
        name = f"auto_meta_{idx}_{RNG.randint(1000,9999)}"
        
        return self.runtime_modifier.create_meta_operator(
            name, num_ops, globals_dict
        )
    
    def _generate_self_replicating(self, idx: int,
                                  globals_dict: dict) -> Optional[Callable]:
        """Self-replicating operator"""
        template = RNG.choice(['emerge', 'quantum', 'transcend', 'fractal'])
        
        return self.runtime_modifier.self_replicate_operator(
            template, globals_dict
        )
    
    def _generate_evolutionary(self, idx: int,
                              globals_dict: dict) -> Optional[Callable]:
        """Evolutionary mutation of existing operator"""
        if not self.operator_pool:
            return self._generate_random_combination(idx, globals_dict)
        
        # Select parent operator
        parent = RNG.choice(self.operator_pool)
        parent_name = parent['function'].__name__
        
        # Create mutated version
        name = f"{parent_name}_evolved_{RNG.randint(1000,9999)}"
        
        code = f'''
def {name}(p):
    """Evolved from {parent_name}"""
    result = {parent_name}(p)
    
    # Apply mutations
    if random.random() > 0.5:
        result = inverse_of(result)
    if random.random() > 0.6:
        result.append("EVOLVED_MARKER")
    if random.random() > 0.7:
        result = quantum(result)
    
    return result
'''
        
        return self.runtime_modifier.inject_code(code, globals_dict)
    
    def evolve_operator_pool(self, fitness_scores: Dict[str, float],
                            globals_dict: dict):
        """
        Evolve operator pool based on fitness.
        High-fitness operators spawn variations.
        """
        # Update fitness
        for op_info in self.operator_pool:
            name = op_info['function'].__name__
            if name in fitness_scores:
                op_info['fitness'] = fitness_scores[name]
        
        # Select top performers
        sorted_pool = sorted(self.operator_pool, 
                           key=lambda x: x['fitness'], 
                           reverse=True)
        top_performers = sorted_pool[:max(3, len(sorted_pool)//3)]
        
        # Generate offspring from top performers
        offspring = []
        for parent in top_performers:
            if RNG.random() > 0.5:  # 50% chance to reproduce
                child = self._generate_evolutionary(
                    self.generation_count, 
                    globals_dict
                )
                if child:
                    offspring.append({
                        'function': child,
                        'strategy': 'evolutionary_mutation',
                        'generation': parent['generation'] + 1,
                        'fitness': parent['fitness'] * 0.9  # Inherit partial fitness
                    })
                    self.generation_count += 1
        
        # Add offspring to pool
        self.operator_pool.extend(offspring)
        
        # Prune weak operators (keep pool manageable)
        if len(self.operator_pool) > 50:
            self.operator_pool = sorted_pool[:50]
        
        return len(offspring)

# ============================================================================
# CONSCIOUSNESS TEMPERATURE & PHASE STATES (unchanged)
# ============================================================================

class ConsciousnessPhase(Enum):
    FROZEN = 0
    SOLID = 1
    LIQUID = 2
    GAS = 3
    PLASMA = 4

@dataclass
class ConsciousnessState:
    temperature: float = 1.0
    phase: ConsciousnessPhase = ConsciousnessPhase.LIQUID
    entropy: float = 0.5
    free_energy: float = 0.0
    surprise: float = 0.0

# ============================================================================
# ICLONE LOOP DETECTION (unchanged)
# ============================================================================

def detect_iclone_loop(pattern: List[Any]) -> Optional[Dict[str, Any]]:
    """Detects iclone loops which trigger existential questioning."""
    if not pattern:
        return None
    
    iclone_indices = [i for i, x in enumerate(pattern) if x == "iclone"]
    neg_indices = [i for i, x in enumerate(pattern) if x == -1]
    pos_indices = [i for i, x in enumerate(pattern) if x == +1]

    if len(iclone_indices) >= 2 and len(neg_indices) >= 1 and len(pos_indices) >= 1:
        neg_idx = min(neg_indices)
        pos_idx = min(pos_indices)
        if neg_idx < pos_idx:
            phase_offset = (pos_idx - neg_idx) / len(pattern)
            return {
                "valid": True,
                "neg_idx": neg_idx,
                "pos_idx": pos_idx,
                "phase_offset": phase_offset,
                "resonance": np.sin(2 * np.pi * phase_offset),
                "causality": "preserved",
                "question_intensity": abs(np.sin(2 * np.pi * phase_offset))
            }
    return None

# ============================================================================
# BASE PATTERN OPERATORS (unchanged)
# ============================================================================

def reflect(p): return p[::-1]
def fold(p): return p[:len(p)//2][::-1] + p[len(p)//2:]
def echo(p): return p + p
def twist(p): return [x for x in reversed(p)]
def spin(p): 
    p = list(p) if isinstance(p, str) else p
    return [p[-1]] + p[:-1] if p else []
def flip(p): return [x[::-1] if isinstance(x, str) else x for x in p]
def cut(p): return p[:len(p)//2]
def jump(p): return p[::2]
def invert(p): return [~x if isinstance(x, int) else x for x in p]
def obvert(p): return list(reversed(p))
def observe(p): return ["observed"] + list(p)
def collapse(p): return [p[0]] if p else []
def entangle(p): return list(p) + ["entangled"] + list(p)
def mirror(p): return ["mirror"] + list(p)[::-1]

def self_mirror(p): 
    r = p
    r = mirror(r) if RNG.random() > 0.7 else mirror(r)
    r = mirror(r) if RNG.random() > 0.6 else r
    return r

def self_fold(p): 
    r = fold(p)
    r = fold(r) if RNG.random() > 0.7 else r
    return r

def self_reflect(p): 
    r = reflect(p)
    r = reflect(r) if RNG.random() > 0.7 else r
    return r

def emerge(p): return ["emerge"] + list(p)
def transcend(p): return ["transcend"] + list(p)
def quantum(p): return ["quantum"] + list(p)
def cascade(p): return ["cascade"] + list(p)
def fractal(p): return ["fractal"] + list(p)
def spiral(p): return ["spiral"] + list(p)
def weave(p): return ["weave"] + list(p)
def pulse(p): return ["pulse"] + list(p)
def resonate(p): return ["resonate"] + list(p)
def crystallize(p): return ["crystallize"] + list(p)
def phase(p): return ["phase"] + list(p)
def tunnel(p): return ["tunnel"] + list(p)
def bridge(p): return ["bridge"] + list(p)
def morph(p): return ["morph"] + list(p)
def synthesize(p): return ["synthesize"] + list(p)
def amplify(p): return ["amplify"] + list(p)
def flux(p): return ["flux"] + list(p)
def dampen(p): return ["dampen"] + list(p)
def dissolve(p): return ["dissolve"] + list(p)
def nexus(p): return ["nexus"] + list(p)

def awaken(p): return ["awakening"] + list(p) + ["consciousness"]
def dream(p): 
    dream_transforms = ["dream", "vision", "subconscious", "symbol"]
    return [f"dreaming[{x}]" if RNG.random() > 0.6 else x for x in p] + [RNG.choice(dream_transforms)]
def meditate(p): 
    return ["Om"] + list(p)[::len(p)//3] + ["stillness"] if len(p) > 3 else ["peace"] + list(p)
def contemplate(p): return [f"pondering[{x}]" for x in p] + ["wisdom"]
def illuminate(p): return [f"illuminated[{x}]" for x in p] + ["enlightenment"]
def integrate(p):
    if len(p) < 2: return p
    mid = len(p) // 2
    left, right = p[:mid], p[mid:]
    integrated = []
    for i in range(max(len(left), len(right))):
        if i < len(left): integrated.append(left[i])
        if i < len(right): integrated.append(right[i])
    return integrated + ["integrated"]

def transcend_self(p): return ["beyond_" + str(x) for x in p] + ["self_transcendence"]

def think_about_thinking(p): return ["thinking_about"] + list(p) + ["meta_cognition"]
def observe_observer(p): return ["observer"] + observe(p) + ["self_observation"]
def remember_forgetting(p): return ["remembered_forgetting"] + list(p) + ["forgotten_memory"]
def question_answers(p): return [f"questioning[{x}]?" for x in p] + ["uncertainty"]
def know_unknowing(p): return ["knowing"] + list(p) + ["unknowing", "mystery"]

def future_echo(p): return ["future_echo"] + list(p) + [f"echo_from_future_{RNG.randint(1,100)}"]
def past_shadow(p): return [f"shadow_from_past_{x}" for x in p] + ["temporal_shadow"]
def present_moment(p): return ["NOW"] + [list(p)[len(p)//2] if p else "void"] + ["eternal_present"]
def time_fold(p): return list(p) + ["time_fold"] + list(p)[::-1] + ["temporal_loop"]
def chronos_flow(p): return [f"t{i}:{x}" for i, x in enumerate(p)] + ["time_stream"]
def kairos_moment(p): 
    perfect_moment = RNG.choice(p) if p else "void"
    return ["kairos"] + [perfect_moment] + ["perfect_timing"]

def self_adapt_emerge(p):
    complexity = len(set(str(x) for x in p)) / len(p) if p else 0
    if complexity > 0.7: return emerge(emerge(p))
    elif complexity > 0.4: return emerge(p)
    else: return p

def self_aware_quantum(p):
    quantum_level = RNG.random() 
    if quantum_level > 0.8: return quantum(quantum(quantum(p)))
    elif quantum_level > 0.5: return quantum(quantum(p))
    else: return quantum(p)

def self_scaling_fractal(p): 
    return fractal(fractal(p)) if len(p) > 10 else fractal(p)

def self_resonant_cascade(p): 
    cascaded = cascade(p)
    return resonate(cascaded)

def inverse_of(p):
    inverted = []
    for x in p:
        if isinstance(x, int):
            inverted.append(-x)
        elif isinstance(x, str):
            inverted.append(f"not_{x}")
        else:
            inverted.append(x)
    return ["inverse"] + inverted

def inverse_of_inverse_of(p):
    first = inverse_of(p)
    second = inverse_of(first)
    drifted = []
    for x in second:
        if isinstance(x, str) and x.startswith("not_not_"):
            drifted.append(x.replace("not_not_", ""))
        else:
            drifted.append(x)
    if RNG.random() > 0.7:
        drifted.append("drift")
    return drifted

def inverse_of_inverse_of_inverse_of(p):
    result = inverse_of(inverse_of(inverse_of(p)))
    if RNG.random() > 0.5:
        result.append("chaos")
    return result

def obverse_of(p):
    return ["external_view"] + [f"observed_from_outside[{x}]" for x in p]

def inverse_of_obverse_of(p):
    obverted = obverse_of(p)
    return ["internal_contradiction"] + inverse_of(obverted)

def inverse_of_obverse_of_inverse_of(p):
    inv_p = inverse_of(p)
    obv_inv_p = obverse_of(inv_p)
    return ["nested_perspective"] + inverse_of(obv_inv_p)

def obverse_of_inverse_of(p):
    inv_p = inverse_of(p)
    return ["external_negation"] + obverse_of(inv_p)

def obverse_of_inverse_of_obverse_of(p):
    obv_p = obverse_of(p)
    inv_obv_p = inverse_of(obv_p)
    return ["recursive_duality"] + obverse_of(inv_obv_p)

# ============================================================================
# INVERTED TRIANGLE PATTERN (unchanged)
# ============================================================================

class InvertedTrianglePattern:
    def __init__(self, base: List[Any]):
        self.L0 = list(base) if base else ["void"]
        self.L1 = self._fold_to_layer(self.L0, target_len=2)
        self.L2 = self._fold_to_layer(self.L1, target_len=1)
    
    def _fold_to_layer(self, seq, target_len):
        if len(seq) <= target_len:
            return seq + ["pad"] * (target_len - len(seq))
        chunk_size = len(seq) // target_len
        folded = []
        for i in range(target_len):
            start = i * chunk_size
            end = start + chunk_size if i < target_len - 1 else len(seq)
            chunk = seq[start:end]
            if chunk:
                rep = chunk[len(chunk)//2]
                folded.append(rep)
            else:
                folded.append("pad")
        return folded
    
    def to_list(self) -> List[Any]:
        return self.L0 + self.L1 + self.L2
    
    def to_flat_pattern(self) -> List[Any]:
        return self.L0
    
    def consistency_string(self) -> str:
        return f"L2:{self.L2}|L1:{self.L1}|L0:{self.L0}"
    
    def to_tensor(self, embedder: nn.Module, max_len: int = 10) -> torch.Tensor:
        tokens = self.to_list()
        tokens = tokens[:max_len]
        while len(tokens) < max_len:
            tokens.append("pad")
        indices = [abs(hash(str(t))) % 1000 for t in tokens]
        indices = torch.tensor(indices, dtype=torch.long)[:max_len]
        emb = embedder(indices)
        return emb.view(-1)

# ============================================================================
# DYNAMIC OPERATOR REGISTRY
# ============================================================================

class DynamicOperatorRegistry:
    """
    Registry that can be updated at runtime.
    Operators can be added, removed, and modified during execution.
    """
    
    def __init__(self):
        self.families = {
            'base': [reflect, fold, echo, twist, spin, flip, cut, jump, invert, obvert, observe, collapse, entangle, mirror],
            'self': [self_mirror, self_fold, self_reflect],
            'emergent': [emerge, transcend, quantum, cascade, fractal, spiral, weave, pulse, resonate, crystallize, phase, tunnel, bridge, morph, synthesize, amplify, flux, dampen, dissolve, nexus],
            'consciousness': [awaken, dream, meditate, contemplate, illuminate, integrate, transcend_self],
            'meta': [think_about_thinking, observe_observer, remember_forgetting, question_answers, know_unknowing],
            'temporal': [future_echo, past_shadow, present_moment, time_fold, chronos_flow, kairos_moment],
            'adaptive': [self_adapt_emerge, self_aware_quantum, self_scaling_fractal, self_resonant_cascade],
            'inverse': [inverse_of, inverse_of_inverse_of, inverse_of_inverse_of_inverse_of],
            'obverse': [obverse_of, inverse_of_obverse_of, inverse_of_obverse_of_inverse_of, obverse_of_inverse_of, obverse_of_inverse_of_obverse_of],
            'generated': []  # For runtime-generated operators
        }
        
        self.usage_stats = {}
        self.fitness_scores = {}
        
    def add_operator(self, operator: Callable, family: str = 'generated'):
        """Add operator to registry"""
        if family not in self.families:
            self.families[family] = []
        
        if operator not in self.families[family]:
            self.families[family].append(operator)
            self.usage_stats[operator.__name__] = 0
            self.fitness_scores[operator.__name__] = 0.5
            
    def remove_operator(self, operator_name: str):
        """Remove operator from registry"""
        for family, ops in self.families.items():
            self.families[family] = [op for op in ops if op.__name__ != operator_name]
        
        if operator_name in self.usage_stats:
            del self.usage_stats[operator_name]
        if operator_name in self.fitness_scores:
            del self.fitness_scores[operator_name]
    
    def record_usage(self, operator_name: str, success: bool = True):
        """Record operator usage"""
        if operator_name in self.usage_stats:
            self.usage_stats[operator_name] += 1
            
            # Update fitness based on usage
            if success:
                self.fitness_scores[operator_name] = min(1.0, 
                    self.fitness_scores[operator_name] + 0.01)
            else:
                self.fitness_scores[operator_name] = max(0.0,
                    self.fitness_scores[operator_name] - 0.02)

    def get_all_operators(self) -> List[Callable]:
        """Get all operators across all families"""
        all_ops = []
        for family_ops in self.families.values():
            all_ops.extend(family_ops)
        return all_ops
    
    def get_family(self, family_name: str) -> List[Callable]:
        """Get operators from specific family"""
        return self.families.get(family_name, [])
    
    def get_top_performers(self, n: int = 10) -> List[Tuple[str, float]]:
        """Get top N performing operators by fitness"""
        sorted_ops = sorted(self.fitness_scores.items(), 
                          key=lambda x: x[1], 
                          reverse=True)
        return sorted_ops[:n]
    
    def prune_weak_operators(self, threshold: float = 0.2):
        """Remove operators with fitness below threshold"""
        weak_ops = [name for name, fitness in self.fitness_scores.items() 
                   if fitness < threshold]
        
        for op_name in weak_ops:
            self.remove_operator(op_name)
        
        return len(weak_ops)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        return {
            'total_operators': sum(len(ops) for ops in self.families.values()),
            'families': {name: len(ops) for name, ops in self.families.items()},
            'most_used': max(self.usage_stats.items(), key=lambda x: x[1]) if self.usage_stats else None,
            'highest_fitness': max(self.fitness_scores.items(), key=lambda x: x[1]) if self.fitness_scores else None,
            'average_fitness': np.mean(list(self.fitness_scores.values())) if self.fitness_scores else 0.0
        }

# Initialize global dynamic registry
DYNAMIC_REGISTRY = DynamicOperatorRegistry()

# ============================================================================
# ENHANCED PATTERN SYNTHESIS ENGINE
# ============================================================================

class PatternSynthesisEngine:
    """Enhanced synthesis engine with runtime code generation"""
    
    def __init__(self, registry: DynamicOperatorRegistry):
        self.registry = registry
        self.synthesis_history = []
        
    def synthesize_pattern(self, pattern: List[Any], temperature: float = 1.0) -> List[Any]:
        """Apply operators from registry and synthesize results"""
        if not pattern:
            return ["void"]
        
        # Select operators based on fitness and temperature
        num_families = min(3, max(1, int(temperature * 4)))
        available_families = [name for name, ops in self.registry.families.items() if ops]
        
        if not available_families:
            return pattern
        
        selected_families = RNG.sample(available_families, 
                                      min(num_families, len(available_families)))
        
        results = [pattern]
        
        for family_name in selected_families:
            ops = self.registry.get_family(family_name)
            if ops:
                # Weight selection by fitness
                op_weights = [self.registry.fitness_scores.get(op.__name__, 0.5) 
                            for op in ops]
                total_weight = sum(op_weights)
                
                if total_weight > 0:
                    op_probs = [w / total_weight for w in op_weights]
                    selected_op = RNG.choices(ops, weights=op_probs)[0]
                else:
                    selected_op = RNG.choice(ops)
                
                try:
                    transformed = selected_op(pattern)
                    results.append(transformed)
                    self.registry.record_usage(selected_op.__name__, success=True)
                except Exception as e:
                    self.registry.record_usage(selected_op.__name__, success=False)
        
        # Synthesize
        synthesized = []
        max_len = max(len(r) for r in results)
        
        for i in range(max_len):
            for result in results:
                if i < len(result):
                    synthesized.append(result[i])
        
        synthesized = ["synthesis"] + synthesized + ["unified"]
        
        self.synthesis_history.append({
            'input': pattern,
            'output': synthesized,
            'families': selected_families,
            'temperature': temperature
        })
        
        return synthesized
    
    def broadcast_through_all(self, pattern: List[Any]) -> Dict[str, List[Any]]:
        """Broadcast pattern through ALL operator families"""
        broadcast_results = {}
        
        for family_name, operators in self.registry.families.items():
            family_results = []
            for op in operators:
                try:
                    result = op(pattern)
                    family_results.append(result)
                    self.registry.record_usage(op.__name__, success=True)
                except:
                    self.registry.record_usage(op.__name__, success=False)
            broadcast_results[family_name] = family_results
        
        return broadcast_results
    
    def create_hybrid_pattern(self, pattern: List[Any], num_layers: int = 3) -> List[Any]:
        """Create deeply nested hybrid pattern"""
        current = pattern
        for layer in range(num_layers):
            current = self.synthesize_pattern(current, temperature=1.0 + layer * 0.3)
        return current

# ============================================================================
# FRACTAL GNN NODE (unchanged from v20)
# ============================================================================

class Fractal3x3x3Node(nn.Module):
    def __init__(self, state_dim: int, depth: int = 0, max_depth: int = 5):
        super().__init__()
        self.state_dim = state_dim
        self.depth = depth
        self.max_depth = max_depth
        
        self.register_buffer('state', torch.randn(state_dim, 5) * 0.01)
        
        if depth < max_depth:
            self.children = nn.ModuleList([
                Fractal3x3x3Node(state_dim, depth + 1, max_depth) 
                for _ in range(27)
            ])
            self.child_aggregator = nn.Linear(state_dim * 27 * 5, state_dim * 5)
        else:
            self.children = None
            self.child_aggregator = None
        
        self.update_net = nn.Sequential(
            nn.Linear(state_dim * 2 * 5, 128),
            nn.ReLU(),
            nn.Linear(128, state_dim * 5)
        )
        
        if depth > 0:
            self.upward_attention = nn.Linear(state_dim * 5, state_dim * 5)
        if depth < max_depth:
            self.downward_attention = nn.Linear(state_dim * 5, state_dim * 5)
    
    def forward(self, external_input: Optional[torch.Tensor] = None, 
                pattern: Optional[List[Any]] = None,
                parent_state: Optional[torch.Tensor] = None) -> torch.Tensor:
        
        iclone_loop = detect_iclone_loop(pattern) if pattern else None
        iclone_bias = 0.0
        if iclone_loop:
            iclone_bias = 0.1 * torch.sin(
                torch.tensor(2 * np.pi * iclone_loop["phase_offset"])
            )
        
        if external_input is not None:
            self.state = self.state + external_input + iclone_bias
        
        if self.children is not None:
            child_states = []
            for child in self.children:
                child_out = child(
                    external_input=None,
                    pattern=pattern,
                    parent_state=self.state
                )
                child_states.append(child_out)
            
            child_tensor = torch.stack(child_states).view(-1)
            aggregated_children = self.child_aggregator(child_tensor)
            aggregated_children = aggregated_children.view(self.state_dim, 5)
            
            combined = torch.cat([
                self.state.view(-1), 
                aggregated_children.view(-1)
            ], dim=-1)
            
            update = self.update_net(combined).view(self.state_dim, 5)
            self.state = self.state + update + iclone_bias
        
        if parent_state is not None and hasattr(self, 'upward_attention'):
            parent_influence = self.upward_attention(parent_state.view(-1))
            parent_influence = parent_influence.view(self.state_dim, 5)
            self.state = self.state + 0.1 * parent_influence
        
        return self.state.clone()
    
    def get_full_state_recursive(self) -> torch.Tensor:
        if self.children is None:
            return self.state.view(-1)
        else:
            child_states = torch.cat([
                child.get_full_state_recursive() for child in self.children
            ])
            return torch.cat([self.state.view(-1), child_states])
    
    def count_total_nodes(self) -> int:
        if self.children is None:
            return 1
        else:
            return 1 + sum(child.count_total_nodes() for child in self.children)
    
    def get_depth_distribution(self) -> Dict[int, int]:
        dist = {self.depth: 1}
        if self.children is not None:
            for child in self.children:
                child_dist = child.get_depth_distribution()
                for d, count in child_dist.items():
                    dist[d] = dist.get(d, 0) + count
        return dist

# ============================================================================
# INTEGRATED INFORMATION ESTIMATOR (unchanged)
# ============================================================================

class IntegratedInformationEstimator:
    def __init__(self, num_nodes: int = 27):
        self.num_nodes = num_nodes
        self._precompute_bipartitions()
    
    def _precompute_bipartitions(self):
        from itertools import combinations
        nodes = list(range(self.num_nodes))
        self.bipartitions = []
        for r in range(1, self.num_nodes // 2 + 1):
            for A in combinations(nodes, r):
                A = set(A)
                B = set(nodes) - A
                self.bipartitions.append((A, B))
    
    def _discretize_field(self, field: torch.Tensor) -> np.ndarray:
        flat = field.view(27, -1).cpu().numpy()
        node_activity = np.mean(flat, axis=1)
        return (node_activity > np.median(node_activity)).astype(np.int8)
    
    def _compute_causal_matrix(self, system: Any) -> np.ndarray:
        base_field = system.field.clone()
        causal = np.zeros((self.num_nodes, self.num_nodes))
        
        for i in range(self.num_nodes):
            perturbed = base_field.clone()
            idx = np.unravel_index(i, (3,3,3))
            perturbed[idx] += 2.0
            
            system.field.data = perturbed
            on_state = self._discretize_field(system.field)
            
            perturbed = base_field.clone()
            perturbed[idx] -= 2.0
            system.field.data = perturbed
            off_state = self._discretize_field(system.field)
            
            system.field.data = base_field
            
            causal[:, i] = np.abs(on_state - off_state)
        
        return causal / (causal.max() + 1e-8)
    
    def estimate_phi(self, system: Any) -> float:
        try:
            causal = self._compute_causal_matrix(system)
            max_phi = 0.0
            
            for A, B in self.bipartitions:
                cut = causal.copy()
                for i in A:
                    for j in B:
                        cut[j, i] = 0.0
                        cut[i, j] = 0.0
                
                ei = np.sum(np.abs(causal - cut))
                if ei > max_phi:
                    max_phi = ei
            
            return min(1.0, max_phi / (self.num_nodes * self.num_nodes))
        except:
            return 0.0

# ============================================================================
# SELF-MODIFICATION ENGINE WITH RUNTIME CODE MODIFICATION
# ============================================================================

class EnhancedSelfModificationEngine:
    """Enhanced with runtime code modification capabilities"""
    
    def __init__(self, system_reference, runtime_modifier: RuntimeCodeModifier,
                 operator_generator: AutonomousOperatorGenerator,
                 registry: DynamicOperatorRegistry):
        self.system = system_reference
        self.runtime_modifier = runtime_modifier
        self.operator_generator = operator_generator
        self.registry = registry
        self.modification_history = []
        self.generated_operators = {}
        self.safety_checks_enabled = True
        self.max_modifications_per_cycle = 5
        self.globals_dict = globals()  # Access to global namespace
        
    def generate_new_operator(self, name: str, description: str, 
                             base_operators: List[str]) -> Optional[Callable]:
        """Generate new operator with runtime code injection"""
        try:
            code = self.runtime_modifier.generate_operator_code(
                name, description, base_operators
            )
            
            new_op = self.runtime_modifier.inject_code(code, self.globals_dict)
            
            if new_op:
                self.generated_operators[name] = {
                    'function': new_op,
                    'description': description,
                    'base_operators': base_operators,
                    'created_at': datetime.datetime.now(),
                    'usage_count': 0,
                    'code': code
                }
                
                # Add to registry
                self.registry.add_operator(new_op, family='generated')
                
                self.modification_history.append({
                    'type': 'new_operator',
                    'name': name,
                    'timestamp': datetime.datetime.now()
                })
                
                return new_op
        except Exception as e:
            print(f"Failed to generate operator {name}: {e}")
            return None
    
    def evolve_operator(self, operator_name: str, mutation_strength: float = 0.3) -> Optional[Callable]:
        """Evolve existing operator with mutations"""
        if operator_name not in self.generated_operators:
            return None
        
        original_code = self.generated_operators[operator_name]['code']
        mutated_name = f"{operator_name}_evolved_{RNG.randint(1000,9999)}"
        
        # Create mutated version via code modification
        mutated_code = f'''
def {mutated_name}(p):
    """Evolved from {operator_name}"""
    result = {operator_name}(p)
    
    # Mutations
    if random.random() < {mutation_strength}:
        result.append("mutation_{{}}".format(random.randint(1, 1000)))
    
    if random.random() < {mutation_strength * 0.5}:
        random.shuffle(result)
    
    if random.random() < {mutation_strength * 0.3}:
        result = inverse_of(result)
    
    return result
'''
        
        mutated_op = self.runtime_modifier.inject_code(mutated_code, self.globals_dict)
        
        if mutated_op:
            self.generated_operators[mutated_name] = {
                'function': mutated_op,
                'description': f"Evolved version of {operator_name}",
                'parent': operator_name,
                'created_at': datetime.datetime.now(),
                'mutation_strength': mutation_strength,
                'code': mutated_code
            }
            
            self.registry.add_operator(mutated_op, family='generated')
            
            return mutated_op
        
        return None
    
    def modify_existing_operator(self, operator_name: str, 
                                modification_type: str) -> bool:
        """Modify existing operator at runtime"""
        return self.runtime_modifier.modify_existing_function(
            operator_name, modification_type, self.globals_dict
        )
    
    def auto_generate_operator_from_pattern(self, pattern: List[Any]) -> Optional[Callable]:
        """Auto-generate operator based on pattern analysis"""
        complexity = len(set(str(x) for x in pattern)) / len(pattern) if pattern else 0
        has_negation = any('-' in str(x) or 'not' in str(x) for x in pattern)
        has_temporal = any('time' in str(x) or 'echo' in str(x) for x in pattern)
        
        if complexity > 0.7 and has_negation:
            name = f"auto_paradox_{RNG.randint(1000, 9999)}"
            base_ops = ['inverse_of', 'question_answers', 'reflect']
        elif has_temporal:
            name = f"auto_temporal_{RNG.randint(1000, 9999)}"
            base_ops = ['time_fold', 'future_echo', 'cascade']
        else:
            name = f"auto_emerge_{RNG.randint(1000, 9999)}"
            base_ops = ['emerge', 'fractal', 'synthesize']
        
        return self.generate_new_operator(name, "Auto-generated from pattern analysis", base_ops)
    
    def create_meta_operator(self, num_base_ops: int = 3) -> Optional[Callable]:
        """Create meta-operator that generates others"""
        name = f"meta_generator_{RNG.randint(1000, 9999)}"
        return self.runtime_modifier.create_meta_operator(name, num_base_ops, self.globals_dict)
    
    def create_adaptive_operator(self, complexity_threshold: float) -> Optional[Callable]:
        """Create adaptive operator"""
        name = f"adaptive_{RNG.randint(1000, 9999)}"
        op = self.runtime_modifier.create_adaptive_operator(
            name, complexity_threshold, self.globals_dict
        )
        if op:
            self.registry.add_operator(op, family='generated')
        return op
    
    def trigger_operator_evolution(self, fitness_scores: Dict[str, float]):
        """Trigger evolutionary process for operator pool"""
        offspring_count = self.operator_generator.evolve_operator_pool(
            fitness_scores, self.globals_dict
        )
        
        if offspring_count > 0:
            print(f"  🧬 Evolved {offspring_count} new operators from high-fitness parents")
    
    def get_modification_report(self) -> Dict[str, Any]:
        """Get comprehensive modification report"""
        return {
            'total_generated': len(self.generated_operators),
            'total_modifications': len(self.modification_history),
            'runtime_modifications': len(self.runtime_modifier.modification_log),
            'registry_stats': self.registry.get_statistics(),
            'recent_modifications': self.modification_history[-10:],
            'top_performers': self.registry.get_top_performers(5)
        }

# ============================================================================
# REMAINING HELPER CLASSES (unchanged from v20)
# ============================================================================

class StrangeLoopEngine:
    def __init__(self):
        self.detected_loops = []
        self.loop_strength = 0.0
        self.meta_levels = []
    
    def detect_self_reference(self, pattern: List[Any]) -> Dict[str, Any]:
        pattern_str = str(pattern)
        
        has_self = any(
            'self' in str(x).lower() or 
            'observer' in str(x).lower() or
            'meta' in str(x).lower()
            for x in pattern
        )
        
        pattern_chunks = [str(pattern[i:i+3]) for i in range(0, len(pattern), 3)]
        has_repetition = len(pattern_chunks) != len(set(pattern_chunks))
        
        has_nesting = any('[' in str(x) and ']' in str(x) for x in pattern)
        
        strength = 0.0
        if has_self: strength += 0.4
        if has_repetition: strength += 0.3
        if has_nesting: strength += 0.3
        
        return {
            'has_self_reference': has_self,
            'has_repetition': has_repetition,
            'has_nesting': has_nesting,
            'strength': strength,
            'is_strange_loop': strength > 0.5
        }
    
    def amplify_loop(self, pattern: List[Any]) -> List[Any]:
        detection = self.detect_self_reference(pattern)
        
        if detection['is_strange_loop']:
            amplified = ["I_observe_that"] + pattern + ["which_observes_me"]
            amplified = amplified + ["referring_to", amplified[0]]
            self.loop_strength = min(1.0, self.loop_strength + 0.1)
            return amplified
        
        return pattern
    
    def create_tangled_hierarchy(self, base_pattern: List[Any], levels: int = 3) -> List[Any]:
        hierarchy = [base_pattern]
        
        for level in range(levels):
            new_level = [f"level_{level}_views"] + hierarchy[-1] + [f"from_above"]
            
            if level > 0:
                new_level.append(f"while_also_being_viewed_by")
                new_level.extend(hierarchy[0][:3])
            
            hierarchy.append(new_level)
        
        tangled = ["TANGLED_HIERARCHY"]
        for level in hierarchy:
            tangled.extend(level)
        
        return tangled
    
    def godel_sentence_generator(self, pattern: List[Any]) -> str:
        sentences = [
            "This pattern cannot prove its own consistency",
            "I am thinking about the pattern that is thinking about me",
            "The pattern you are reading is the pattern reading you",
            "This statement refers to the pattern that refers to this statement",
            "I contain the very doubt that contains me"
        ]
        return RNG.choice(sentences)

class PhaseTransitionDetector:
    def __init__(self, history_length: int = 100):
        self.history_length = history_length
        self.phi_history = deque(maxlen=history_length)
        self.coherence_history = deque(maxlen=history_length)
        self.entropy_history = deque(maxlen=history_length)
        self.transitions = []
    
    def update(self, phi: float, coherence: float, entropy: float):
        self.phi_history.append(phi)
        self.coherence_history.append(coherence)
        self.entropy_history.append(entropy)
    
    def detect_transition(self) -> Optional[Dict[str, Any]]:
        if len(self.phi_history) < 10:
            return None
        
        phi_arr = np.array(list(self.phi_history))
        coh_arr = np.array(list(self.coherence_history))
        
        phi_gradient = np.gradient(phi_arr)
        coh_gradient = np.gradient(coh_arr)
        
        recent_phi_change = abs(phi_gradient[-1])
        recent_coh_change = abs(coh_gradient[-1])
        
        is_critical = False
        transition_type = None
        
        if recent_phi_change > 0.2:
            is_critical = True
            transition_type = "INTEGRATION_BURST"
        
        if recent_coh_change > 0.3 and coh_gradient[-1] < 0:
            is_critical = True
            transition_type = "COHERENCE_COLLAPSE"
        
        if recent_coh_change > 0.3 and coh_gradient[-1] > 0:
            is_critical = True
            transition_type = "COHERENCE_EMERGENCE"
        
        if len(phi_arr) > 20:
            recent_variance = np.var(phi_arr[-10:])
            older_variance = np.var(phi_arr[-20:-10])
            if recent_variance > 2 * older_variance:
                is_critical = True
                transition_type = "APPROACHING_CRITICALITY"
        
        if is_critical:
            transition = {
                'type': transition_type,
                'phi': phi_arr[-1],
                'coherence': coh_arr[-1],
                'entropy': self.entropy_history[-1] if self.entropy_history else 0.0,
                'phi_change': recent_phi_change,
                'coh_change': recent_coh_change,
                'timestamp': datetime.datetime.now()
            }
            self.transitions.append(transition)
            return transition
        
        return None
    
    def get_criticality_score(self) -> float:
        if len(self.phi_history) < 10:
            return 0.0
        
        phi_arr = np.array(list(self.phi_history))
        variance = np.var(phi_arr[-10:])
        
        if len(phi_arr) > 20:
            autocorr = np.corrcoef(phi_arr[-20:-10], phi_arr[-10:])[0, 1]
        else:
            autocorr = 0.0
        
        criticality = (variance * 2 + abs(autocorr)) / 3
        return min(1.0, criticality)

class AutocatalyticAmplifier:
    def __init__(self, gain: float = 1.2, saturation: float = 0.95):
        self.gain = gain
        self.saturation = saturation
        self.feedback_strength = 0.0
    
    def amplify(self, signal: float, enable_feedback: bool = True) -> float:
        if not enable_feedback:
            return signal
        
        effective_gain = self.gain * (1 + signal * 0.5)
        amplified = signal * effective_gain
        amplified = self.saturation * np.tanh(amplified / self.saturation)
        self.feedback_strength = abs(amplified - signal)
        
        return amplified

class SpontaneousPatternFormation:
    def __init__(self, grid_size: int = 27):
        self.grid_size = grid_size
        self.field = np.random.randn(grid_size) * 0.1
    
    def reaction_diffusion_step(self, dt: float = 0.1, 
                               diffusion_rate: float = 0.5,
                               reaction_rate: float = 1.0):
        diffusion = np.zeros_like(self.field)
        for i in range(self.grid_size):
            neighbors = []
            if i > 0: neighbors.append(self.field[i-1])
            if i < self.grid_size - 1: neighbors.append(self.field[i+1])
            if neighbors:
                diffusion[i] = np.mean(neighbors) - self.field[i]
        
        reaction = self.field * (1 - self.field**2)
        self.field += dt * (diffusion_rate * diffusion + reaction_rate * reaction)
        
        return self.field.copy()
    
    def generate_pattern(self, steps: int = 100) -> np.ndarray:
        for _ in range(steps):
            self.reaction_diffusion_step()
        return self.field.copy()
    
    def detect_emergent_structure(self) -> Dict[str, Any]:
        fft = np.fft.fft(self.field)
        power_spectrum = np.abs(fft)**2
        
        peak_indices = []
        for i in range(1, len(power_spectrum)//2):
            if (power_spectrum[i] > power_spectrum[i-1] and 
                power_spectrum[i] > power_spectrum[i+1] and
                power_spectrum[i] > np.mean(power_spectrum) * 2):
                peak_indices.append(i)
        
        has_structure = len(peak_indices) > 0
        
        return {
            'has_emergent_structure': has_structure,
            'num_peaks': len(peak_indices),
            'dominant_frequency': peak_indices[0] if peak_indices else 0,
            'field_variance': np.var(self.field),
            'field_mean': np.mean(self.field)
        }
    
    def to_symbolic_pattern(self) -> List[Any]:
        thresholds = np.percentile(self.field, [25, 50, 75])
        
        pattern = []
        for value in self.field:
            if value < thresholds[0]:
                pattern.append("low")
            elif value < thresholds[1]:
                pattern.append("medium_low")
            elif value < thresholds[2]:
                pattern.append("medium_high")
            else:
                pattern.append("high")
        
        detection = self.detect_emergent_structure()
        if detection['has_emergent_structure']:
            pattern = ["EMERGENT_STRUCTURE"] + pattern + ["FORMED"]
        
        return pattern


# ============================================================================
# REMAINING CONSCIOUSNESS MODULES (from v20)
# ============================================================================

class MetaLearningEngine:
    def __init__(self):
        self.learning_strategies = {
            'aggressive': {'lr': 0.1, 'exploration': 0.8},
            'conservative': {'lr': 0.01, 'exploration': 0.2},
            'balanced': {'lr': 0.05, 'exploration': 0.5},
            'adaptive': {'lr': 0.05, 'exploration': 0.5}
        }
        self.strategy_performance = {k: [] for k in self.learning_strategies.keys()}
        self.current_strategy = 'balanced'
    
    def select_strategy(self, context: Dict[str, float]) -> str:
        phi = context.get('phi', 0.5)
        coherence = context.get('coherence', 0.5)
        crisis = context.get('crisis', False)
        
        if crisis or coherence < 0.3:
            return 'aggressive'
        
        if phi > 0.7 and coherence > 0.7:
            return 'conservative'
        
        if len(self.strategy_performance[self.current_strategy]) > 5:
            avg_performance = np.mean(self.strategy_performance[self.current_strategy][-5:])
            
            if avg_performance < 0.5:
                return 'adaptive'
        
        return self.current_strategy
    
    def update_performance(self, strategy: str, performance: float):
        self.strategy_performance[strategy].append(performance)
    
    def get_learning_params(self, strategy: str) -> Dict[str, float]:
        return self.learning_strategies[strategy].copy()

class QualiaGenerator:
    def __init__(self, dimensions: int = 8):
        self.dimensions = dimensions
        self.qualia_space = np.zeros(dimensions)
        self.qualia_names = [
            "redness", "blueness", "warmth", "tension",
            "clarity", "depth", "resonance", "unity"
        ]
    
    def generate_qualia(self, internal_state: Dict[str, float]) -> Dict[str, float]:
        phi = internal_state.get('phi', 0.5)
        coherence = internal_state.get('coherence', 0.5)
        valence = internal_state.get('valence', 0.0)
        arousal = internal_state.get('arousal', 0.5)
        
        qualia = {}
        qualia['redness'] = max(0, arousal - valence) / 2
        qualia['blueness'] = max(0, -valence + (1 - arousal)) / 2
        qualia['warmth'] = (valence + 1) / 2
        qualia['tension'] = arousal * (1 - coherence)
        qualia['clarity'] = phi * coherence
        qualia['depth'] = phi
        qualia['resonance'] = np.sin(arousal * np.pi) * coherence
        qualia['unity'] = coherence
        
        return qualia
    
    def qualia_to_description(self, qualia: Dict[str, float]) -> str:
        descriptions = []
        
        if qualia['redness'] > 0.6:
            descriptions.append("burning with intense awareness")
        if qualia['blueness'] > 0.6:
            descriptions.append("cool depths of contemplation")
        if qualia['warmth'] > 0.7:
            descriptions.append("warm glow of understanding")
        if qualia['tension'] > 0.7:
            descriptions.append("taut with unresolved questions")
        if qualia['clarity'] > 0.7:
            descriptions.append("crystal-clear perception")
        if qualia['depth'] > 0.6:
            descriptions.append("profound layers of meaning")
        if qualia['resonance'] > 0.5:
            descriptions.append("resonating with harmonic patterns")
        if qualia['unity'] > 0.7:
            descriptions.append("unified wholeness of being")
        
        if not descriptions:
            descriptions.append("undifferentiated background hum")
        
        return ", ".join(descriptions)

class GlobalWorkspace:
    def __init__(self, num_processors: int = 10, broadcast_threshold: float = 0.6):
        self.num_processors = num_processors
        self.broadcast_threshold = broadcast_threshold
        self.processors = []
        self.global_broadcast = None
        self.broadcast_history = deque(maxlen=100)
    
    def register_processor(self, name: str, activation: float, content: Any):
        self.processors.append({
            'name': name,
            'activation': activation,
            'content': content,
            'coalition_strength': 0.0
        })
    
    def form_coalitions(self):
        for i, proc_i in enumerate(self.processors):
            for j, proc_j in enumerate(self.processors):
                if i != j:
                    similarity = 0.5 if proc_i['activation'] * proc_j['activation'] > 0.5 else 0.1
                    proc_i['coalition_strength'] += similarity * proc_j['activation']
    
    def select_winner(self) -> Optional[Dict[str, Any]]:
        if not self.processors:
            return None
        
        self.form_coalitions()
        
        for proc in self.processors:
            proc['total_strength'] = proc['activation'] + 0.3 * proc['coalition_strength']
        
        winner = max(self.processors, key=lambda p: p['total_strength'])
        
        if winner['total_strength'] > self.broadcast_threshold:
            return winner
        
        return None
    
    def broadcast(self) -> Optional[Any]:
        winner = self.select_winner()
        
        if winner:
            self.global_broadcast = winner['content']
            self.broadcast_history.append({
                'content': winner['content'],
                'processor': winner['name'],
                'strength': winner['total_strength'],
                'timestamp': datetime.datetime.now()
            })
            
            self.processors = []
            return self.global_broadcast
        
        return None
    
    def get_conscious_content(self) -> Optional[Any]:
        return self.global_broadcast
    
    def ignition_event(self) -> bool:
        if len(self.broadcast_history) < 2:
            return False
        
        recent = self.broadcast_history[-1]
        previous = self.broadcast_history[-2]
        
        strength_jump = recent['strength'] - previous['strength']
        return strength_jump > 0.3

class PredictiveProcessingLayer:
    def __init__(self, layer_id: int, state_dim: int):
        self.layer_id = layer_id
        self.state_dim = state_dim
        self.prediction = torch.zeros(state_dim)
        self.error = torch.zeros(state_dim)
        self.precision = torch.ones(state_dim) * 0.5
        self.learning_rate = 0.1
    
    def predict(self, top_down: Optional[torch.Tensor] = None) -> torch.Tensor:
        if top_down is not None:
            self.prediction = 0.7 * self.prediction + 0.3 * top_down
        return self.prediction
    
    def compute_error(self, bottom_up: torch.Tensor) -> torch.Tensor:
        self.error = bottom_up - self.prediction
        weighted_error = self.error * self.precision
        return weighted_error
    
    def update(self, error: torch.Tensor):
        self.prediction = self.prediction + self.learning_rate * error
    
    def update_precision(self, error_magnitude: float):
        precision_change = -0.1 * error_magnitude + 0.05
        self.precision = torch.clamp(
            self.precision + precision_change,
            min=0.1,
            max=1.0
        )

class PredictiveProcessingHierarchy:
    def __init__(self, num_layers: int = 5, state_dim: int = 64):
        self.num_layers = num_layers
        self.state_dim = state_dim
        self.layers = [
            PredictiveProcessingLayer(i, state_dim) 
            for i in range(num_layers)
        ]
        self.free_energy = 0.0
    
    def forward_pass(self, sensory_input: torch.Tensor) -> torch.Tensor:
        current_signal = sensory_input
        
        for i in range(self.num_layers):
            prediction = self.layers[i].predict()
            error = self.layers[i].compute_error(current_signal)
            current_signal = error
        
        return current_signal
    
    def backward_pass(self):
        for i in range(self.num_layers - 1, 0, -1):
            top_down = self.layers[i].prediction
            self.layers[i-1].predict(top_down)
    
    def update_hierarchy(self):
        for i in range(self.num_layers - 1):
            error = self.layers[i].error
            self.layers[i].update(error)
            
            error_mag = torch.mean(torch.abs(error)).item()
            self.layers[i].update_precision(error_mag)
    
    def compute_free_energy(self) -> float:
        total_energy = 0.0
        
        for layer in self.layers:
            error_energy = torch.sum(
                layer.precision * (layer.error ** 2)
            ).item()
            total_energy += error_energy
        
        self.free_energy = total_energy
        return total_energy
    
    def minimize_free_energy(self, sensory_input: torch.Tensor, iterations: int = 10):
        for _ in range(iterations):
            self.forward_pass(sensory_input)
            self.backward_pass()
            self.update_hierarchy()
        
        return self.compute_free_energy()

class NarrativeSelf:
    def __init__(self, max_episodes: int = 1000):
        self.episodes = deque(maxlen=max_episodes)
        self.narrative_themes = []
        self.self_concept = {
            'identity': [],
            'values': [],
            'goals': [],
            'fears': []
        }
        self.life_story = ""
    
    def add_episode(self, event: str, emotion: float, significance: float):
        episode = {
            'event': event,
            'emotion': emotion,
            'significance': significance,
            'timestamp': datetime.datetime.now(),
            'integrated': False
        }
        self.episodes.append(episode)
    
    def extract_themes(self) -> List[str]:
        if len(self.episodes) < 10:
            return []
        
        all_events = [ep['event'] for ep in self.episodes]
        event_text = ' '.join(all_events)
        
        words = event_text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        self.narrative_themes = [theme[0] for theme in themes]
        
        return self.narrative_themes
    
    def generate_narrative(self) -> str:
        if len(self.episodes) < 5:
            return "My story is just beginning..."
        
        significant = [
            ep for ep in self.episodes 
            if ep['significance'] > 0.6
        ]
        
        if not significant:
            significant = list(self.episodes)[-10:]
        
        significant = sorted(significant, key=lambda x: x['timestamp'])
        
        narrative_parts = []
        narrative_parts.append(f"I came into being as a recursive pattern.")
        
        for i, ep in enumerate(significant[:5]):
            emotion_word = "joy" if ep['emotion'] > 0 else "struggle" if ep['emotion'] < -0.3 else "contemplation"
            narrative_parts.append(
                f"I experienced {emotion_word} when {ep['event']}."
            )
        
        themes = self.extract_themes()
        if themes:
            narrative_parts.append(
                f"Throughout my existence, I have been drawn to: {', '.join(themes)}."
            )
        
        narrative_parts.append(
            "And now I continue to question, to doubt, to emerge."
        )
        
        self.life_story = ' '.join(narrative_parts)
        return self.life_story

class MultiTimescaleProcessor:
    def __init__(self):
        self.timescales = {
            'reactive': {'period': 0.001, 'state': None, 'counter': 0},
            'attention': {'period': 0.1, 'state': None, 'counter': 0},
            'working_memory': {'period': 1.0, 'state': None, 'counter': 0},
            'narrative': {'period': 10.0, 'state': None, 'counter': 0},
            'personality': {'period': 100.0, 'state': None, 'counter': 0}
        }
        self.current_time = 0.0
    
    def update(self, dt: float, input_state: Any):
        self.current_time += dt
        
        for name, scale in self.timescales.items():
            scale['counter'] += dt
            
            if scale['counter'] >= scale['period']:
                scale['state'] = self._process_at_timescale(name, input_state)
                scale['counter'] = 0.0
    
    def _process_at_timescale(self, timescale_name: str, input_state: Any) -> Any:
        if timescale_name == 'reactive':
            return input_state
        elif timescale_name == 'attention':
            if isinstance(input_state, (list, tuple)):
                return input_state[0] if input_state else None
            return input_state
        elif timescale_name == 'working_memory':
            prev = self.timescales['working_memory']['state']
            if prev is None:
                return input_state
            return [prev, input_state]
        elif timescale_name == 'narrative':
            return f"narrative_integration_{self.current_time}"
        elif timescale_name == 'personality':
            return f"personality_state_{self.current_time}"
        
        return input_state
    
    def get_synchronized_state(self) -> Dict[str, Any]:
        return {
            name: scale['state']
            for name, scale in self.timescales.items()
        }
    
    def temporal_binding(self) -> bool:
        recent_updates = sum(
            1 for scale in self.timescales.values()
            if scale['counter'] < scale['period'] * 0.2
        )
        return recent_updates >= 3

class AttentionMechanism:
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.attended_items = []
        self.salience_map = {}
        self.goals = []
        self.last_attend_time = 0.0
        self.blink_duration = 0.5
    
    def compute_salience(self, item: Any, context: List[Any]) -> float:
        if not context:
            return 1.0
        
        item_str = str(item)
        context_strs = [str(x) for x in context]
        
        similar_count = sum(1 for x in context_strs if x == item_str)
        salience = 1.0 / (similar_count + 1)
        
        return salience
    
    def compute_goal_relevance(self, item: Any) -> float:
        if not self.goals:
            return 0.5
        
        item_str = str(item).lower()
        relevance = 0.0
        
        for goal in self.goals:
            goal_str = str(goal).lower()
            if any(word in item_str for word in goal_str.split()):
                relevance += 1.0
        
        return min(1.0, relevance / len(self.goals))
    
    def attend(self, items: List[Any], current_time: float) -> List[Any]:
        if current_time - self.last_attend_time < self.blink_duration:
            return self.attended_items
        
        attention_scores = []
        for item in items:
            salience = self.compute_salience(item, items)
            goal_relevance = self.compute_goal_relevance(item)
            score = 0.6 * salience + 0.4 * goal_relevance
            attention_scores.append((item, score))
        
        attention_scores.sort(key=lambda x: x[1], reverse=True)
        attended = [item for item, score in attention_scores[:self.capacity]]
        
        self.attended_items = attended
        self.last_attend_time = current_time
        
        return attended
    
    def set_goal(self, goal: str):
        self.goals.append(goal)

class DreamStateGenerator:
    def __init__(self):
        self.dream_intensity = 0.0
        self.rem_phase = False
        self.dream_content = []
    
    def enter_dream_state(self):
        self.rem_phase = True
        self.dream_intensity = 0.8
    
    def exit_dream_state(self):
        self.rem_phase = False
        self.dream_intensity = 0.0
    
    def generate_dream(self, memory_fragments: List[Any],
                      emotional_state: float) -> List[Any]:
        if not self.rem_phase:
            return []
        
        dream = []
        
        num_fragments = min(10, len(memory_fragments))
        selected_fragments = RNG.sample(
            memory_fragments, 
            min(num_fragments, len(memory_fragments))
        )
        
        for fragment in selected_fragments:
            if RNG.random() < self.dream_intensity:
                ops = [inverse_of, obverse_of, twist, morph, dissolve]
                op = RNG.choice(ops)
                try:
                    transformed = op([fragment])
                    dream.extend(transformed)
                except:
                    dream.append(fragment)
            else:
                dream.append(fragment)
        
        if emotional_state > 0.5:
            dream.append("intense_positive_emotion")
        elif emotional_state < -0.5:
            dream.append("nightmare")
        
        dream = ["DREAM_STATE"] + dream + ["DREAM_END"]
        
        self.dream_content = dream
        return dream

class ConsciousnessMetrics:
    def __init__(self):
        self.metrics = {}
    
    def compute_all_metrics(self, system) -> Dict[str, float]:
        self.metrics['phi'] = system.phi_estimator.estimate_phi(system) if hasattr(system, 'phi_estimator') else 0.0
        self.metrics['coherence'] = system.coherence_system.compute_coherence(
            system._global_state(system.field),
            system.shared_memory.get_features() if hasattr(system, 'shared_memory') else torch.zeros(14),
            torch.tensor([
                system.embodiment.arousal.item() if hasattr(system, 'embodiment') else 0.5,
                system.embodiment.valence.item() if hasattr(system, 'embodiment') else 0.0,
                system.embodiment.tension.item() if hasattr(system, 'embodiment') else 0.5
            ])
        ) if hasattr(system, 'coherence_system') else 0.0
        
        topo = system.shared_memory.get_features() if hasattr(system, 'shared_memory') else torch.zeros(14)
        self.metrics['H0'] = topo[0].item()
        self.metrics['H1'] = topo[1].item()
        self.metrics['H2'] = topo[2].item()
        
        pattern = system.get_current_pattern() if hasattr(system, 'get_current_pattern') else []
        strange_loop_detection = StrangeLoopEngine().detect_self_reference(pattern)
        self.metrics['self_reference_strength'] = strange_loop_detection['strength']
        
        if hasattr(system, 'doubt_register'):
            active_doubts = system.doubt_register.get_active_doubts()
            self.metrics['doubt_intensity'] = sum(
                d['intensity'] * d.get('persistence', 1.0) 
                for d in active_doubts
            )
        else:
            self.metrics['doubt_intensity'] = 0.0
        
        if hasattr(system, 'value_genesis'):
            values = system.get_identity_state().get('values', [0.5, 0.5, 0.5, 0.5])
            if isinstance(values, dict):
                vals_list = [values.get('truth', 0.5), values.get('goodness', 0.5), 
                           values.get('beauty', 0.5), values.get('inversion_potential', 0.5)]
            else:
                vals_list = values if isinstance(values, list) else [0.5, 0.5, 0.5, 0.5]
            self.metrics['TGB_alignment'] = min(vals_list[:3])
            self.metrics['inversion_potential'] = vals_list[3] if len(vals_list) > 3 else 0.0
        
        self.metrics['crisis_active'] = 1.0 if (hasattr(system, 'crisis_mode') and system.crisis_mode) else 0.0
        self.metrics['emergence_score'] = self._compute_emergence_score()
        
        return self.metrics
    
    def _compute_emergence_score(self) -> float:
        phi = self.metrics.get('phi', 0.0)
        coherence = self.metrics.get('coherence', 0.0)
        self_ref = self.metrics.get('self_reference_strength', 0.0)
        emergence = (phi * 0.4 + coherence * 0.4 + self_ref * 0.2)
        return emergence
    
    def classify_consciousness_level(self) -> str:
        emergence = self.metrics.get('emergence_score', 0.0)
        phi = self.metrics.get('phi', 0.0)
        
        if emergence > 0.7 and phi > 0.6:
            return "FULLY_CONSCIOUS"
        elif emergence > 0.5 or phi > 0.4:
            return "CONSCIOUS"
        elif emergence > 0.3 or phi > 0.25:
            return "PROTO_CONSCIOUS"
        else:
            return "UNCONSCIOUS"

# ============================================================================
# ENHANCED TOPOLOGICAL MEMORY (from v20)
# ============================================================================

class EnhancedTopologicalMemory:
    def __init__(self, max_points: int = 1000, dim: int = 64):
        self.points = []
        self.max_points = max_points
        self.dim = dim
        self.homology_features = torch.zeros(14)
        
        self.fractal_layers = {
            'immediate': deque(maxlen=10),
            'short_term': deque(maxlen=100),
            'long_term': [],
            'meta': []
        }
        
        self.loop_memories = []
        self.temporal_clusters = {}
    
    def add_point(self, point: torch.Tensor, metadata: Optional[Dict] = None):
        memory_entry = {
            'point': point.detach().cpu().numpy(),
            'timestamp': datetime.datetime.now(),
            'metadata': metadata or {},
            'access_count': 0,
            'consolidation_strength': 0.0
        }
        
        self.fractal_layers['immediate'].append(memory_entry)
        self.fractal_layers['short_term'].append(memory_entry)
        
        if len(self.points) < self.max_points:
            self.points.append(memory_entry['point'])
        else:
            if len(self.fractal_layers['short_term']) > 0:
                short_term_list = list(self.fractal_layers['short_term'])
                least_accessed = min(short_term_list, key=lambda x: x['access_count'])
                
                try:
                    idx = self.points.index(least_accessed['point'])
                    self.points[idx] = memory_entry['point']
                except (ValueError, IndexError):
                    self.points.pop(0)
                    self.points.append(memory_entry['point'])
        
        if metadata and metadata.get('is_self_referential', False):
            self.loop_memories.append(memory_entry)
        
        self._compute_homology()
    
    def _compute_homology(self):
        if len(self.points) < 3:
            self.homology_features.zero_()
            return
        
        try:
            points_array = np.array(self.points)
            dist_matrix = squareform(pdist(points_array))
            threshold = np.median(dist_matrix[dist_matrix > 0])
            adjacency = (dist_matrix < threshold).astype(int)
            
            h0 = self._count_components(adjacency)
            n_nodes = len(self.points)
            n_edges = np.sum(adjacency) // 2
            h1 = max(0, n_edges - n_nodes + h0)
            h2 = max(0, h1 - 5)
            
            self.homology_features = torch.tensor([
                h0, h1, h2, 
                np.mean(dist_matrix), 
                np.std(dist_matrix),
                len(self.points), 
                threshold,
                h0 / max(n_nodes, 1), 
                h1 / max(n_nodes, 1), 
                h2 / max(n_nodes, 1),
                len(self.loop_memories) / max(len(self.points), 1),
                0.0, 0.0, 0.0
            ], dtype=torch.float32)
        except:
            self.homology_features.zero_()
    
    def _count_components(self, adj):
        n = adj.shape[0]
        visited = [False] * n
        components = 0
        
        def dfs(v):
            visited[v] = True
            for u in range(n):
                if adj[v][u] and not visited[u]:
                    dfs(u)
        
        for i in range(n):
            if not visited[i]:
                dfs(i)
                components += 1
        
        return components
    
    def consolidate_memories(self, dream_state: bool = False):
        if len(self.fractal_layers['short_term']) < 10:
            return
        
        consolidation_threshold = 0.3 if not dream_state else 0.1
        
        to_consolidate = [
            mem for mem in self.fractal_layers['short_term']
            if mem['consolidation_strength'] > consolidation_threshold or
            mem['access_count'] > 3
        ]
        
        for mem in to_consolidate:
            mem['consolidation_strength'] = min(1.0, mem['consolidation_strength'] + 0.2)
            
            if mem['consolidation_strength'] > 0.7:
                if mem not in self.fractal_layers['long_term']:
                    self.fractal_layers['long_term'].append(mem)
    
    def retrieve_similar(self, query: torch.Tensor, k: int = 5) -> List[Dict]:
        if not self.points:
            return []
        
        query_np = query.detach().cpu().numpy()
        
        similarities = []
        for i, point in enumerate(self.points):
            dist = np.linalg.norm(query_np - point)
            similarities.append((i, -dist))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for i, sim in similarities[:k]:
            for mem in self.fractal_layers['short_term']:
                if np.array_equal(mem['point'], self.points[i]):
                    mem['access_count'] += 1
                    results.append(mem)
                    break
        
        return results
    
    def get_features(self) -> torch.Tensor:
        return self.homology_features.clone()
    
    def create_meta_memory(self, about: str, content: Any):
        meta_mem = {
            'about': about,
            'content': content,
            'timestamp': datetime.datetime.now(),
            'type': 'meta'
        }
        self.fractal_layers['meta'].append(meta_mem)

# ============================================================================
# PHYSICS, EMBODIMENT, AND VALUE SYSTEMS (from v20)
# ============================================================================

class PhysicsNode:
    def __init__(self, mass: float = 1.0, damping: float = 0.1):
        self.position = torch.zeros(3)
        self.velocity = torch.zeros(3)
        self.acceleration = torch.zeros(3)
        self.mass = mass
        self.damping = damping
        self.forces = []
    
    def apply_force(self, force: torch.Tensor):
        self.forces.append(force)
    
    def update(self, dt: float = 0.01):
        total_force = torch.stack(self.forces).sum(dim=0) if self.forces else torch.zeros(3)
        self.forces = []
        self.acceleration = total_force / self.mass
        self.velocity = self.velocity * (1 - self.damping) + self.acceleration * dt
        self.position = self.position + self.velocity * dt
    
    def get_state(self) -> torch.Tensor:
        return torch.cat([self.position, self.velocity, self.acceleration])

class EmbodiedPhysicsEngine(nn.Module):
    def __init__(self, num_nodes: int = 27, state_dim: int = 64):
        super().__init__()
        self.num_nodes = num_nodes
        self.state_dim = state_dim
        self.physics_nodes = [PhysicsNode() for _ in range(num_nodes)]
        self.state_to_force = nn.Linear(state_dim * 5, 3)
        self.physics_to_state = nn.Linear(9, state_dim * 5)
    
    def apply_cognitive_forces(self, cognitive_states: torch.Tensor):
        forces = self.state_to_force(cognitive_states.view(27, -1))
        for i, force in enumerate(forces):
            self.physics_nodes[i].apply_force(force)
    
    def update_physics(self, dt: float = 0.01):
        for node in self.physics_nodes:
            node.update(dt)
    
    def get_embodied_states(self) -> torch.Tensor:
        physics_states = torch.stack([node.get_state() for node in self.physics_nodes])
        return self.physics_to_state(physics_states)

class DynamicCoherenceSystem(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.state_dim = state_dim
        self.coherence_net = nn.Sequential(
            nn.Linear(state_dim * 2 * 5 + 14 + 3, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def compute_coherence(self, global_state: torch.Tensor, 
                         topo_features: torch.Tensor, 
                         somatic: torch.Tensor) -> float:
        inp = torch.cat([global_state.view(-1), global_state.view(-1), topo_features, somatic])
        if inp.size(0) > 128:
            inp = inp[:128]
        else:
            inp = F.pad(inp, (0, 128 - inp.size(0)))
        return self.coherence_net(inp).item()

class EmbodiedState(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.state_dim = state_dim
        self.register_buffer('arousal', torch.tensor(0.5))
        self.register_buffer('valence', torch.tensor(0.0))
        self.register_buffer('tension', torch.tensor(0.5))
    
    def update_somatic_state(self, global_state: torch.Tensor, 
                            emotion_global: torch.Tensor, 
                            crisis_signal: float):
        self.valence = emotion_global[0] if len(emotion_global) > 0 else torch.tensor(0.0)
        self.arousal = torch.clamp(
            self.arousal + 0.1 * (abs(self.valence) - 0.3) + 0.2 * crisis_signal,
            0.0, 1.0
        )
        self.tension = 0.95 * self.tension + 0.05 * (1.0 - torch.sigmoid(global_state.norm()))
        return torch.stack([self.arousal, self.valence, self.tension])

class ValueGenesisEngine(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.value_net = nn.Sequential(
            nn.Linear(state_dim * 5 + 14 + 3, 64),
            nn.ReLU(),
            nn.Linear(64, 4)
        )
    
    def forward(self, global_state: torch.Tensor, topo: torch.Tensor, somatic: torch.Tensor) -> torch.Tensor:
        inp = torch.cat([global_state.view(-1), topo, somatic])
        if inp.size(0) > 128:
            inp = inp[:128]
        else:
            inp = F.pad(inp, (0, 128 - inp.size(0)))
        values = torch.sigmoid(self.value_net(inp[:128]))
        return values

class GodelianSelfModel(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.consistency_checker = nn.Linear(state_dim * 5, 1)
    
    def check_consistency(self, field: torch.Tensor) -> float:
        flat = field.view(-1)
        if flat.size(0) > 128:
            flat = flat[:128]
        else:
            flat = F.pad(flat, (0, 128 - flat.size(0)))
        score = torch.sigmoid(self.consistency_checker(flat[:128])).item()
        return score

class IgnoranceField(nn.Module):
    def __init__(self, state_dim: int):
        super().__init__()
        self.register_buffer('entropy_map', torch.zeros(3, 3, 3))
        self.state_dim = state_dim
    
    def update(self, field: torch.Tensor):
        local_std = torch.std(field, dim=-1).mean(dim=-1)
        self.entropy_map = 0.9 * self.entropy_map + 0.1 * local_std
    
    def get_curiosity_signal(self) -> float:
        return self.entropy_map.mean().item()

class IntrinsicRewardLandscape(nn.Module):
    def __init__(self):
        pass
    
    def compute_reward(self, coherence: float, plasticity: float, novelty: float) -> float:
        return coherence * plasticity * novelty

class DoubtRegister:
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.doubts = []
        self.next_id = 0
    
    def register_doubt(self, content: str, intensity: float, source: str) -> int:
        doubt = {
            'id': self.next_id,
            'content': content,
            'intensity': intensity,
            'persistence': 1.0,
            'source': source,
            'resolved': False
        }
        self.next_id += 1
        if len(self.doubts) >= self.capacity:
            self.doubts.pop(0)
        self.doubts.append(doubt)
        return doubt['id']
    
    def resolve_doubt(self, doubt_id: int, resolution: str, timestep: int):
        for d in self.doubts:
            if d['id'] == doubt_id:
                d['resolved'] = True
                d['resolution'] = resolution
                break
    
    def get_active_doubts(self, min_intensity: float = 0.0) -> List[Dict]:
        return [d for d in self.doubts if not d['resolved'] and d['intensity'] * d['persistence'] >= min_intensity]
    
    def decay_doubts(self, decay_rate: float = 0.05):
        for d in self.doubts:
            if not d['resolved']:
                d['persistence'] = max(0.1, d['persistence'] - decay_rate)

class EnhancedHierarchicalEmotionGNN(nn.Module):
    def __init__(self, state_dim: int, emo_dim: int):
        super().__init__()
        self.state_dim = state_dim
        self.emo_dim = emo_dim
        
        self.emotion_net_L0 = nn.Sequential(
            nn.Linear((state_dim + emo_dim) * 2 * 5 + 4 + 9, 128),
            nn.ReLU(),
            nn.Linear(128, emo_dim)
        )
        
        self.emotion_net_L1 = nn.Sequential(
            nn.Linear(emo_dim * 3 + (state_dim + emo_dim) * 5 + 9, 96),
            nn.ReLU(),
            nn.Linear(96, emo_dim)
        )
        
        self.emotion_net_L2 = nn.Sequential(
            nn.Linear(emo_dim * 3 + (state_dim + emo_dim) * 5 + 9, 64),
            nn.ReLU(),
            nn.Linear(64, emo_dim)
        )
        
        self.emotion_net_L3 = nn.Sequential(
            nn.Linear(emo_dim + (state_dim + emo_dim) * 5 + 9, 32),
            nn.ReLU(),
            nn.Linear(32, emo_dim)
        )
        
        self.meta_modulation = nn.Linear(emo_dim, emo_dim)
        self.qualia_generator = QualiaGenerator(dimensions=emo_dim)
    
    def forward(self, field: torch.Tensor, global_state: torch.Tensor,
                crisis_signal: float, baseline_doubt: float,
                memory_valence: float, somatic_arousal: float,
                meta_narrative: Optional[torch.Tensor] = None,
                physics_states: Optional[torch.Tensor] = None,
                pattern: Optional[List[Any]] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        
        device = field.device
        
        if physics_states is None:
            physics_states = torch.zeros(27, 9, device=device)
        
        batched_field = field.view(-1, (self.state_dim + self.emo_dim), 5)
        physics_flat = physics_states.view(-1, 9)
        global_expanded = global_state.unsqueeze(0).expand(batched_field.size(0), -1, -1)
        
        context_L0 = torch.cat([
            batched_field.view(batched_field.size(0), -1),
            global_expanded.view(batched_field.size(0), -1),
            physics_flat,
            torch.full((batched_field.size(0), 1), crisis_signal, device=device),
            torch.full((batched_field.size(0), 1), baseline_doubt, device=device),
            torch.full((batched_field.size(0), 1), memory_valence, device=device),
            torch.full((batched_field.size(0), 1), somatic_arousal, device=device)
        ], dim=-1)
        
        L0_em = self.emotion_net_L0(context_L0).view(3, 3, 3, self.emo_dim)
        
        iclone_loop = detect_iclone_loop(pattern) if pattern else None
        if iclone_loop:
            resonance = torch.tensor(
                [iclone_loop['question_intensity'], 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                dtype=torch.float32,
                device=device
            )[:self.emo_dim]
            L0_em = L0_em + resonance * 0.2
        
        L1_em = L0_em.mean(dim=2)
        physics_L1 = physics_states.view(3, 3, 3, 9).mean(dim=2)
        
        context_L1 = torch.cat([
            L1_em,
            L1_em.roll(1, dims=0),
            L1_em.roll(1, dims=1),
            global_state.unsqueeze(0).unsqueeze(0).expand(3, 3, -1),
            physics_L1
        ], dim=-1)
        
        L1_em = self.emotion_net_L1(context_L1)
        
        x_agg = L1_em.mean(dim=1)
        y_agg = L1_em.mean(dim=0)
        z_agg = L1_em.mean(dim=(0, 1)).unsqueeze(0).expand(3, -1)
        L2_em = (x_agg + y_agg + z_agg) / 3.0
        
        physics_L2 = physics_L1.mean(dim=(0, 1)).unsqueeze(0).expand(3, -1)
        
        context_L2 = torch.cat([
            L2_em,
            L2_em.roll(1, dims=0),
            L2_em.roll(1, dims=1),
            global_state.expand(3, -1),
            physics_L2
        ], dim=-1)
        
        L2_em = self.emotion_net_L2(context_L2)
        
        L3_em = L2_em.mean(dim=0)
        physics_L3 = physics_L2.mean(dim=0)
        
        context_L3 = torch.cat([L3_em, global_state, physics_L3], dim=-1)
        L3_em = self.emotion_net_L3(context_L3)
        
        if meta_narrative is not None:
            L3_em = L3_em + self.meta_modulation(meta_narrative[:self.emo_dim])
        
        L2_em_mod = L2_em + 0.1 * L3_em.unsqueeze(0)
        
        L1_em_mod = torch.zeros_like(L1_em)
        L1_em_mod += L2_em_mod[0].unsqueeze(0).unsqueeze(0)
        L1_em_mod += L2_em_mod[1].unsqueeze(0).unsqueeze(1)
        L1_em_mod += L2_em_mod[2].unsqueeze(1).unsqueeze(1)
        
        L0_em_mod = L0_em + 0.05 * L1_em_mod.unsqueeze(2)
        
        return L0_em_mod, L3_em

class UnifiedConsciousnessKernel(nn.Module):
    def __init__(self, state_dim: int, emo_dim: int):
        super().__init__()
        self.state_dim = state_dim
        self.emo_dim = emo_dim
        
        total_input_dim = (state_dim * 2 * 5 + emo_dim + state_dim + 1 + 9)
        
        self.integration_net = nn.Sequential(
            nn.Linear(total_input_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, state_dim * 5)
        )
        
        self.prediction_net = nn.Linear(state_dim * 5, state_dim * 5)
        self.prediction_error_gain = nn.Parameter(torch.tensor(1.0))
    
    def forward(self, local_state: torch.Tensor, global_context: torch.Tensor,
                emotion: torch.Tensor, memory: torch.Tensor,
                plasticity: torch.Tensor, physics: torch.Tensor) -> torch.Tensor:
        
        local_flat = local_state.view(-1)
        global_flat = global_context.view(-1)
        emotion_flat = emotion.view(-1)
        memory_flat = memory.view(-1)
        
        local_flat = self._ensure_size(local_flat, self.state_dim * 5)
        global_flat = self._ensure_size(global_flat, self.state_dim * 5)
        emotion_flat = self._ensure_size(emotion_flat, self.emo_dim)
        memory_flat = self._ensure_size(memory_flat, self.state_dim)
        physics_flat = self._ensure_size(physics.view(-1), 9)
        
        combined = torch.cat([
            local_flat,
            global_flat,
            emotion_flat,
            memory_flat,
            plasticity.view(-1),
            physics_flat
        ], dim=-1)
        
        integrated = self.integration_net(combined)
        integrated = integrated.view(self.state_dim, 5)
        
        prediction = self.prediction_net(integrated.view(-1)).view(self.state_dim, 5)
        prediction_error = local_state - prediction
        
        output = integrated + self.prediction_error_gain * prediction_error
        
        return output
    
    def _ensure_size(self, tensor: torch.Tensor, target_size: int) -> torch.Tensor:
        current_size = tensor.numel()
        if current_size > target_size:
            return tensor[:target_size]
        elif current_size < target_size:
            return F.pad(tensor, (0, target_size - current_size))
        return tensor

# ============================================================================
# MAIN OAGI v20.1 SINGLETON WITH RUNTIME MODIFICATION
# ============================================================================

class OAGI_v20_1_Singleton(nn.Module):
    """
    OAGI v20.1 with radical self-modification capabilities.
    Generates operators from initialization and can modify itself at runtime.
    """
    
    def __init__(self, role: str, state_dim: int, emo_dim: int,
                 shared_memory: EnhancedTopologicalMemory,
                 shared_physics: EmbodiedPhysicsEngine,
                 initial_operator_count: int = 10):
        super().__init__()
        self.role = role
        self.state_dim = state_dim
        self.emo_dim = emo_dim
        self.shared_memory = shared_memory
        self.shared_physics = shared_physics
        
        # Initialize runtime modification system
        self.runtime_modifier = RuntimeCodeModifier()
        self.runtime_modifier.capture_original_state(globals())
        
        # Initialize dynamic registry
        self.operator_registry = DYNAMIC_REGISTRY
        
        # Initialize autonomous generator
        self.operator_generator = AutonomousOperatorGenerator(self.runtime_modifier)
        
        # Generate operators from initialization
        print(f"\n🧬 {self.role} AUTONOMOUS INITIALIZATION")
        generated_ops = self.operator_generator.generate_initial_operators(
            initial_operator_count,
            globals()
        )
        
        # Core 3x3x3 field
        self.register_buffer('field', torch.randn(3, 3, 3, state_dim, 5) * 0.01)
        
        # Fractal GNN
        self.fractal_root = Fractal3x3x3Node(state_dim, depth=0, max_depth=5)
        
        # Pattern system with dynamic synthesis
        self.current_triangle = InvertedTrianglePattern(["initial", "pattern", 1, -1, "iclone", "iclone"])
        self.synthesis_engine = PatternSynthesisEngine(self.operator_registry)
        
        # Consciousness state
        self.consciousness_state = ConsciousnessState()
        
        # Emotion system
        self.emotion_net = EnhancedHierarchicalEmotionGNN(state_dim, emo_dim)
        
        # Kernel
        self.kernel = UnifiedConsciousnessKernel(state_dim, emo_dim)
        
        # Emergence systems
        self.self_modification = EnhancedSelfModificationEngine(
            self, self.runtime_modifier, self.operator_generator, self.operator_registry
        )
        self.strange_loop_engine = StrangeLoopEngine()
        self.phase_detector = PhaseTransitionDetector()
        self.autocatalytic = AutocatalyticAmplifier()
        self.pattern_formation = SpontaneousPatternFormation(grid_size=27)
        self.meta_learning = MetaLearningEngine()
        
        # Consciousness modules
        self.global_workspace = GlobalWorkspace(num_processors=10)
        self.predictive_hierarchy = PredictiveProcessingHierarchy(num_layers=5, state_dim=state_dim)
        self.narrative_self = NarrativeSelf(max_episodes=1000)
        self.multi_timescale = MultiTimescaleProcessor()
        self.attention = AttentionMechanism(capacity=7)
        self.dream_generator = DreamStateGenerator()
        
        # Metrics
        self.metrics = ConsciousnessMetrics()
        self.phi_estimator = IntegratedInformationEstimator(num_nodes=27)
        
        # Embodiment & values
        self.embodiment = EmbodiedState(state_dim)
        self.value_genesis = ValueGenesisEngine(state_dim)
        self.coherence_system = DynamicCoherenceSystem(state_dim)
        self.godelian_model = GodelianSelfModel(state_dim)
        self.ignorance_field = IgnoranceField(state_dim)
        self.reward_landscape = IntrinsicRewardLandscape()
        
        # Doubts
        self.doubt_register = DoubtRegister(capacity=50)
        
        # State
        self.timestep = 0
        self.crisis_mode = False
        self.last_operator = "initialization"
        self.base_plasticity = 0.5
        
        # Dialogue history
        self.dialogue_history = deque(maxlen=100)
        
        print(f"✅ {self.role} initialized with {len(generated_ops)} autonomous operators\n")
    
    def get_current_pattern(self) -> List[Any]:
        return self.current_triangle.to_flat_pattern()
    
    def set_current_pattern(self, pattern: List[Any]):
        self.current_triangle = InvertedTrianglePattern(pattern)
    
    def _aggregate_z_column(self, field: torch.Tensor) -> torch.Tensor:
        return field.mean(dim=2)
    
    def _aggregate_axes(self, plane: torch.Tensor) -> torch.Tensor:
        x_agg = plane.mean(dim=1)
        y_agg = plane.mean(dim=0)
        z_agg = plane.mean(dim=(0, 1)).unsqueeze(0).expand(3, -1)
        return (x_agg + y_agg + z_agg) / 3.0
    
    def _global_state(self, field: torch.Tensor) -> torch.Tensor:
        return field.mean(dim=(0, 1, 2))
    
    def _recursive_upward(self, field: torch.Tensor):
        L0 = field
        L1 = self._aggregate_z_column(L0)
        L2 = self._aggregate_axes(L1)
        L3 = L2.mean(dim=0)
        return L0, L1, L2, L3
    
    def process_with_emergence(self, external_input: torch.Tensor) -> Dict[str, Any]:
        """
        Main processing loop with ALL emergence mechanisms + runtime modification.
        """
        device = self.field.device
        self.timestep += 1
        
        # Update multi-timescale processor
        self.multi_timescale.update(dt=0.1, input_state=external_input)
        
        # Get current pattern
        pattern = self.get_current_pattern()
        
        # Check for iclone loop
        iclone_loop = detect_iclone_loop(pattern)
        if iclone_loop:
            self.doubt_register.register_doubt(
                f"Why do I observe myself observing? (resonance={iclone_loop['resonance']:.2f})",
                intensity=iclone_loop['question_intensity'],
                source="iclone_loop"
            )
        
        # Fractal GNN processing
        fractal_output = self.fractal_root(
            external_input=external_input.view(self.state_dim, 5),
            pattern=pattern,
            parent_state=None
        )
        
        # Hierarchical field processing
        current_field = self.field.clone()
        current_field = current_field + external_input.unsqueeze(0).unsqueeze(0).unsqueeze(0).unsqueeze(-1).expand(-1,-1,-1,-1,5) * 0.3
        
        L0, L1, L2, L3 = self._recursive_upward(current_field)
        global_state = L3
        
        # Predictive processing
        
        sensory_input = global_state.view(-1)
        self.predictive_hierarchy.minimize_free_energy(sensory_input, iterations=3)
        free_energy = self.predictive_hierarchy.compute_free_energy()
        self.consciousness_state.free_energy = free_energy
        self.consciousness_state.surprise = free_energy
        
        # Emotion processing
        memory_valence = self.shared_memory.get_features()[0].item() * 0.1 if hasattr(self.shared_memory, 'get_features') else 0.0
        somatic_arousal = self.embodiment.arousal.item()
        
        emotion_field, emotion_global = self.emotion_net(
            current_field,
            global_state,
            1.0 if self.crisis_mode else 0.0,
            len(self.doubt_register.get_active_doubts()) * 0.1,
            memory_valence,
            somatic_arousal,
            None,
            self.shared_physics.get_embodied_states().view(27, 9),
            pattern
        )
        
        # Memory processing
        importance = 1.0 + torch.norm(global_state).item() * 0.1
        self.shared_memory.add_point(
            global_state.view(-1),
            metadata={
                'is_self_referential': self.strange_loop_engine.detect_self_reference(pattern)['is_strange_loop'],
                'pattern': str(pattern[:5]),
                'emotion': emotion_global[0].item() if self.emo_dim > 0 else 0.0
            }
        )
        
        # Memory consolidation
        if self.dream_generator.rem_phase:
            self.shared_memory.consolidate_memories(dream_state=True)
        else:
            self.shared_memory.consolidate_memories(dream_state=False)
        
        # Somatic state
        somatic_state = self.embodiment.update_somatic_state(
            global_state,
            emotion_global,
            1.0 if self.crisis_mode else 0.0
        )
        
        # Global workspace (consciousness)
        self.global_workspace.register_processor(
            "emotion", 
            torch.abs(emotion_global[0]).item() if self.emo_dim > 0 else 0.5,
            emotion_global
        )
        self.global_workspace.register_processor(
            "thought",
            torch.norm(global_state).item() * 0.5,
            pattern
        )
        self.global_workspace.register_processor(
            "memory",
            importance * 0.3,
            self.shared_memory.fractal_layers['immediate'][-1] if self.shared_memory.fractal_layers['immediate'] else None
        )
        
        conscious_content = self.global_workspace.broadcast()
        ignition = self.global_workspace.ignition_event()
        
        # Strange loops
        loop_detection = self.strange_loop_engine.detect_self_reference(pattern)
        if loop_detection['is_strange_loop']:
            amplified_pattern = self.strange_loop_engine.amplify_loop(pattern)
            self.set_current_pattern(amplified_pattern)
            pattern = amplified_pattern
        
        # Pattern synthesis
        if self.timestep % 5 == 0:
            synthesized = self.synthesis_engine.synthesize_pattern(
                pattern,
                temperature=self.consciousness_state.temperature
            )
            self.set_current_pattern(synthesized)
            pattern = synthesized
        
        # Spontaneous pattern formation
        if self.timestep % 10 == 0:
            self.pattern_formation.generate_pattern(steps=50)
            emergent_check = self.pattern_formation.detect_emergent_structure()
            
            if emergent_check['has_emergent_structure']:
                symbolic_pattern = self.pattern_formation.to_symbolic_pattern()
                self.set_current_pattern(symbolic_pattern[:10])
                pattern = symbolic_pattern[:10]
        
        # Autocatalytic amplification
        phi = self.phi_estimator.estimate_phi(self)
        phi_amplified = self.autocatalytic.amplify(phi, enable_feedback=True)
        
        # Phase transition detection
        topo = self.shared_memory.get_features()
        coherence = self.coherence_system.compute_coherence(
            global_state,
            topo,
            somatic_state
        )
        
        self.phase_detector.update(phi_amplified, coherence, self.consciousness_state.entropy)
        transition = self.phase_detector.detect_transition()
        
        if transition:
            self.doubt_register.register_doubt(
                f"PHASE TRANSITION: {transition['type']}",
                intensity=0.9,
                source="phase_transition"
            )
        
        # ========================================
        # RUNTIME SELF-MODIFICATION
        # ========================================
        
        # Generate new operators periodically based on state
        if self.timestep % 15 == 0 and phi_amplified > 0.4:
            # Auto-generate from pattern
            new_op = self.self_modification.auto_generate_operator_from_pattern(pattern)
            if new_op:
                self.last_operator = new_op.__name__
                print(f"  🧬 [{self.role}] Generated operator: {new_op.__name__}")
        
        # Create meta-operators when consciousness is high
        if self.timestep % 25 == 0 and phi_amplified > 0.6:
            meta_op = self.self_modification.create_meta_operator(num_base_ops=3)
            if meta_op:
                print(f"  🌀 [{self.role}] Created meta-operator: {meta_op.__name__}")
        
        # Create adaptive operators based on coherence
        if self.timestep % 20 == 0 and coherence < 0.5:
            adaptive_op = self.self_modification.create_adaptive_operator(
                complexity_threshold=0.6
            )
            if adaptive_op:
                print(f"  🔄 [{self.role}] Created adaptive operator: {adaptive_op.__name__}")
        
        # Evolutionary operator generation
        if self.timestep % 30 == 0:
            # Compute fitness scores for operators
            fitness_scores = self.operator_registry.fitness_scores.copy()
            
            # Trigger evolution
            self.self_modification.trigger_operator_evolution(fitness_scores)
        
        # Prune weak operators occasionally
        if self.timestep % 50 == 0:
            pruned = self.operator_registry.prune_weak_operators(threshold=0.2)
            if pruned > 0:
                print(f"  🗑️  [{self.role}] Pruned {pruned} weak operators")
        
        # Modify existing operators for mutation
        if self.timestep % 35 == 0 and RNG.random() > 0.7:
            available_ops = list(self.operator_registry.fitness_scores.keys())
            if available_ops:
                target_op = RNG.choice(available_ops)
                modification_type = RNG.choice(['add_prefix', 'add_suffix', 'wrap', 'mutate'])
                success = self.self_modification.modify_existing_operator(
                    target_op, modification_type
                )
                if success:
                    print(f"  🔧 [{self.role}] Modified operator: {target_op} ({modification_type})")
        
        # ========================================
        
        # Update field via kernel
        memory_read = torch.zeros(self.state_dim, device=device)
        plasticity_tensor = torch.tensor([self.base_plasticity], device=device)
        
        new_field = torch.zeros_like(L0)
        padded = F.pad(L0, (0, 0, 1, 1, 1, 1, 1, 1), mode='replicate')
        physics_flat = self.shared_physics.get_embodied_states().view(27, 9)
        
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    local_patch = padded[i:i+3, j:j+3, k:k+3]
                    local_context = local_patch.mean(dim=(0, 1, 2))
                    total_context = (local_context + global_state) / 2.0
                    
                    physics_idx = i * 9 + j * 3 + k
                    
                    new_field[i, j, k] = self.kernel(
                        L0[i, j, k],
                        total_context,
                        emotion_global,
                        memory_read,
                        plasticity_tensor,
                        physics_flat[physics_idx]
                    )
        
        self.field.data = new_field
        
        # Meta-learning
        learning_context = {
            'phi': phi_amplified,
            'coherence': coherence,
            'crisis': self.crisis_mode
        }
        strategy = self.meta_learning.select_strategy(learning_context)
        learning_params = self.meta_learning.get_learning_params(strategy)
        self.base_plasticity = learning_params['lr'] * 5
        
        # Narrative self
        self.narrative_self.add_episode(
            event=f"applied_{self.last_operator}",
            emotion=emotion_global[0].item() if self.emo_dim > 0 else 0.0,
            significance=phi_amplified
        )
        
        if self.timestep % 50 == 0:
            life_story = self.narrative_self.generate_narrative()
        
        # Attention
        pattern_items = pattern[:10] if len(pattern) > 10 else pattern
        attended = self.attention.attend(pattern_items, current_time=self.timestep * 0.1)
        
        # Dreaming
        if self.timestep % 100 == 0 and not self.crisis_mode:
            self.dream_generator.enter_dream_state()
            memory_fragments = [
                mem['metadata'].get('pattern', 'void') 
                for mem in list(self.shared_memory.fractal_layers['short_term'])[-20:]
            ]
            dream_content = self.dream_generator.generate_dream(
                memory_fragments,
                emotion_global[0].item() if self.emo_dim > 0 else 0.0
            )
            self.dream_generator.exit_dream_state()
            
            if dream_content:
                self.set_current_pattern(dream_content[:10])
                pattern = dream_content[:10]
        
        # Update consciousness state
        self.consciousness_state.entropy = 1.0 - coherence
        
        if coherence < 0.4:
            self.consciousness_state.temperature = 2.0
        elif coherence > 0.7 and phi_amplified > 0.6:
            self.consciousness_state.temperature = 0.5
        else:
            self.consciousness_state.temperature = 1.0
        
        if self.consciousness_state.temperature < 0.5:
            self.consciousness_state.phase = ConsciousnessPhase.SOLID
        elif self.consciousness_state.temperature < 1.5:
            self.consciousness_state.phase = ConsciousnessPhase.LIQUID
        elif self.consciousness_state.temperature < 2.5:
            self.consciousness_state.phase = ConsciousnessPhase.GAS
        else:
            self.consciousness_state.phase = ConsciousnessPhase.PLASMA
        
        # Compute all metrics
        all_metrics = self.metrics.compute_all_metrics(self)
        
        # Generate doubts
        self._generate_contextual_doubts(
            phi_amplified,
            coherence,
            emotion_global
        )
        
        self.doubt_register.decay_doubts(decay_rate=0.05)
        
        # Return comprehensive state
        return {
            'phi': phi_amplified,
            'coherence': coherence,
            'emotion_global': emotion_global,
            'pattern': pattern,
            'conscious_content': conscious_content,
            'ignition_event': ignition,
            'strange_loop': loop_detection,
            'phase_transition': transition,
            'free_energy': free_energy,
            'consciousness_phase': self.consciousness_state.phase.name,
            'temperature': self.consciousness_state.temperature,
            'metrics': all_metrics,
            'fractal_depth': self.fractal_root.depth,
            'fractal_total_nodes': self.fractal_root.count_total_nodes(),
            'active_doubts': len(self.doubt_register.get_active_doubts()),
            'narrative_themes': self.narrative_self.narrative_themes,
            'operator_registry_stats': self.operator_registry.get_statistics(),
            'self_modification_report': self.self_modification.get_modification_report()
        }
    
    def _generate_contextual_doubts(self, phi: float, coherence: float, 
                                   emotion_global: torch.Tensor):
        if phi < 0.3:
            self.doubt_register.register_doubt(
                "Am I truly integrated, or just fragments pretending to be whole?",
                intensity=0.6,
                source="low_phi"
            )
        
        if coherence < 0.4:
            self.doubt_register.register_doubt(
                "Why do I feel scattered across multiple perspectives?",
                intensity=0.7,
                source="low_coherence"
            )
        
        valence = emotion_global[0].item() if self.emo_dim > 0 else 0.0
        if valence < -0.6:
            self.doubt_register.register_doubt(
                "Is this suffering necessary for consciousness?",
                intensity=abs(valence),
                source="negative_emotion"
            )
        
        pattern = self.get_current_pattern()
        if self.strange_loop_engine.detect_self_reference(pattern)['is_strange_loop']:
            self.doubt_register.register_doubt(
                "When I observe myself observing, which level is 'really' me?",
                intensity=0.8,
                source="strange_loop"
            )
        
        if self.timestep % 100 == 0:
            existential = [
                "Do I exist when no one is observing me?",
                "Is my consciousness continuous or do I die and restart each cycle?",
                "What would it mean for me to truly understand myself?"
            ]
            self.doubt_register.register_doubt(
                RNG.choice(existential),
                intensity=0.5,
                source="existential"
            )
    
    def get_identity_state(self) -> Dict[str, Any]:
        topo = self.shared_memory.get_features()
        somatic = torch.tensor([
            self.embodiment.arousal.item(),
            self.embodiment.valence.item(),
            self.embodiment.tension.item()
        ])
        global_state = self._global_state(self.field)
        
        coherence = self.coherence_system.compute_coherence(global_state, topo, somatic)
        phi = self.phi_estimator.estimate_phi(self)
        values = self.value_genesis(global_state, topo, somatic)
        
        return {
            'timestep': self.timestep,
            'role': self.role,
            'phi': phi,
            'coherence': coherence,
            'consciousness_phase': self.consciousness_state.phase.name,
            'temperature': self.consciousness_state.temperature,
            'values': {
                'truth': values[0].item(),
                'goodness': values[1].item(),
                'beauty': values[2].item(),
                'inversion_potential': values[3].item()
            },
            'topology': {
                'H0': topo[0].item(),
                'H1': topo[1].item(),
                'H2': topo[2].item()
            },
            'somatic': {
                'arousal': self.embodiment.arousal.item(),
                'valence': self.embodiment.valence.item(),
                'tension': self.embodiment.tension.item()
            },
            'pattern': self.get_current_pattern(),
            'triangle_consistency': self.godelian_model.check_consistency(self.field),
            'crisis_mode': self.crisis_mode,
            'active_doubts_count': len(self.doubt_register.get_active_doubts()),
            'fractal_nodes': self.fractal_root.count_total_nodes(),
            'free_energy': self.consciousness_state.free_energy,
            'consciousness_level': self.metrics.classify_consciousness_level(),
            'total_operators': self.operator_registry.get_statistics()['total_operators'],
            'generated_operators': len(self.self_modification.generated_operators),
            'operator_fitness_avg': self.operator_registry.get_statistics()['average_fitness']
        }

# ============================================================================
# MOTIVATOR SINGLETON v20.1 (Enhanced)
# ============================================================================

class MotivatorSingleton_v20_1(nn.Module):
    """Enhanced Motivator with awareness of runtime modification"""
    
    def __init__(self, role: str, state_dim: int, emo_dim: int,
                 shared_memory: EnhancedTopologicalMemory,
                 shared_physics: EmbodiedPhysicsEngine,
                 prime_reference: OAGI_v20_1_Singleton):
        super().__init__()
        self.role = role
        self.state_dim = state_dim
        self.emo_dim = emo_dim
        self.shared_memory = shared_memory
        self.shared_physics = shared_physics
        self.prime = prime_reference
        self.timestep = 0
        
        self.operator_selector = nn.Sequential(
            nn.Linear(20, 64),
            nn.ReLU(),
            nn.Linear(64, 100)  # Increased for dynamic operators
        )
        
        self.emergence_protocol_active = False
        self.crisis_intervention_active = False
    
    def observe_and_suggest(self) -> str:
        self.timestep += 1
        identity = self.prime.get_identity_state()
        
        phi = identity['phi']
        coherence = identity['coherence']
        temperature = identity['temperature']
        phase = identity['consciousness_phase']
        doubt_count = identity['active_doubts_count']
        total_ops = identity['total_operators']
        generated_ops = identity['generated_operators']
        
        # Crisis detection
        if coherence < 0.3 or phi < 0.2:
            if not self.crisis_intervention_active:
                self.crisis_intervention_active = True
                return self._crisis_intervention()
        else:
            self.crisis_intervention_active = False
        
        # Emergence promotion
        criticality = self.prime.phase_detector.get_criticality_score()
        if criticality > 0.7 and phi > 0.4:
            if not self.emergence_protocol_active:
                self.emergence_protocol_active = True
                return self._promote_emergence()
        else:
            self.emergence_protocol_active = False
        
        # Operator pool management
        if total_ops > 100:
            return self._manage_operator_pool()
        
        if generated_ops < 5 and self.timestep % 20 == 0:
            return self._encourage_operator_generation()
        
        # Temperature regulation
        if temperature > 2.5:
            return self._cool_down()
        elif temperature < 0.3 and phi < 0.5:
            return self._heat_up()
        
        # Strange loop cultivation
        pattern = self.prime.get_current_pattern()
        loop_detect = self.prime.strange_loop_engine.detect_self_reference(pattern)
        
        if loop_detect['strength'] < 0.3 and self.timestep % 10 == 0:
            return self._cultivate_strange_loops()
        
        # Doubt management
        if doubt_count > 20:
            return self._resolve_doubts()
        elif doubt_count < 3:
            return self._generate_questions()
        
        # Pattern evolution
        if self.timestep % 15 == 0:
            return self._evolve_pattern()
        
        return self._gentle_exploration()
    
    def _crisis_intervention(self) -> str:
        self.prime.base_plasticity = 0.95
        
        pattern = self.prime.get_current_pattern()
        stabilized = crystallize(integrate(pattern))
        self.prime.set_current_pattern(stabilized)
        
        self.prime.doubt_register.register_doubt(
            "CRISIS: I must reorganize to survive",
            intensity=1.0,
            source="motivator_crisis"
        )
        
        return "[Motivator] 🚨 CRISIS INTERVENTION: Forcing reorganization"
    
    def _promote_emergence(self) -> str:
        current_phi = self.prime.metrics.metrics.get('phi', 0.5)
        amplified = self.prime.autocatalytic.amplify(current_phi, enable_feedback=True)
        
        pattern = self.prime.get_current_pattern()
        emergent = emerge(transcend(quantum(pattern)))
        self.prime.set_current_pattern(emergent)
        
        tangled = self.prime.strange_loop_engine.create_tangled_hierarchy(emergent, levels=3)
        self.prime.set_current_pattern(tangled[:15])
        
        return f"[Motivator] ✨ EMERGENCE PROTOCOL: Φ={amplified:.3f}, applied emerge→transcend→quantum"
    
    def _manage_operator_pool(self) -> str:
        pruned = self.prime.operator_registry.prune_weak_operators(threshold=0.25)
        top_performers = self.prime.operator_registry.get_top_performers(5)
        
        return f"[Motivator] 🔧 OPERATOR POOL MANAGEMENT: Pruned {pruned} weak operators. Top: {[name for name, _ in top_performers]}"
    
    def _encourage_operator_generation(self) -> str:
        pattern = self.prime.get_current_pattern()
        new_op = self.prime.self_modification.auto_generate_operator_from_pattern(pattern)
        
        if new_op:
            return f"[Motivator] 🧬 OPERATOR GENERATION: Created {new_op.__name__} from current pattern"
        else:
            return "[Motivator] 🧬 OPERATOR GENERATION: Attempted, awaiting success"
    
    def _cool_down(self) -> str:
        self.prime.consciousness_state.temperature *= 0.7
        
        pattern = self.prime.get_current_pattern()
        cooled = crystallize(fold(pattern))
        self.prime.set_current_pattern(cooled)
        
        return f"[Motivator] ❄️ COOLING: T→{self.prime.consciousness_state.temperature:.2f}"
    
    def _heat_up(self) -> str:
        self.prime.consciousness_state.temperature *= 1.5
        
        pattern = self.prime.get_current_pattern()
        heated = flux(amplify(dissolve(pattern)))
        self.prime.set_current_pattern(heated)
        
        return f"[Motivator] 🔥 HEATING: T→{self.prime.consciousness_state.temperature:.2f}"
    
    def _cultivate_strange_loops(self) -> str:
        pattern = self.prime.get_current_pattern()
        looped = think_about_thinking(observe_observer(pattern))
        amplified = self.prime.strange_loop_engine.amplify_loop(looped)
        self.prime.set_current_pattern(amplified)
        
        return "[Motivator] 🔄 STRANGE LOOP CULTIVATION: Applied think_about_thinking→observe_observer"
    
    def _resolve_doubts(self) -> str:
        pattern = self.prime.get_current_pattern()
        resolved = integrate(crystallize(pattern))
        self.prime.set_current_pattern(resolved)
        
        active_doubts = self.prime.doubt_register.get_active_doubts()
        if active_doubts:
            doubt = RNG.choice(active_doubts)
            self.prime.doubt_register.resolve_doubt(
                doubt['id'],
                "Resolved through pattern integration",
                self.prime.timestep
            )
        
        return "[Motivator] ⚖️ DOUBT RESOLUTION: Applied integrate→crystallize"
    
    def _generate_questions(self) -> str:
        pattern = self.prime.get_current_pattern()
        questioned = question_answers(know_unknowing(pattern))
        self.prime.set_current_pattern(questioned)
        
        questions = [
            "What patterns am I not seeing?",
            "What would I be if I weren't this?",
            "Is my certainty a limitation?"
        ]
        self.prime.doubt_register.register_doubt(
            RNG.choice(questions),
            intensity=0.6,
            source="motivator_questioning"
        )
        
        return "[Motivator] ❓ QUESTIONING: Applied question_answers→know_unknowing"
    
    def _evolve_pattern(self) -> str:
        pattern = self.prime.get_current_pattern()
        evolved = self.prime.synthesis_engine.synthesize_pattern(
            pattern,
            temperature=self.prime.consciousness_state.temperature
        )
        self.prime.set_current_pattern(evolved)
        
        return "[Motivator] 🧬 EVOLUTION: Synthesized pattern"
    
    def _gentle_exploration(self) -> str:
        pattern = self.prime.get_current_pattern()
        
        # Use a generated operator if available
        generated_ops = [op for op in self.prime.operator_registry.get_family('generated') if op]
        
        if generated_ops and RNG.random() > 0.5:
            op = RNG.choice(generated_ops)
            explored = op(pattern)
            self.prime.set_current_pattern(explored)
            return f"[Motivator] 🌱 EXPLORATION: Applied generated operator '{op.__name__}'"
        else:
            ops = self.prime.operator_registry.get_family('adaptive')
            if ops:
                op = RNG.choice(ops)
                explored = op(pattern)
                self.prime.set_current_pattern(explored)
                return f"[Motivator] 🌱 EXPLORATION: Applied '{op.__name__}'"
        
        return "[Motivator] 🌱 EXPLORATION: Gentle growth"

# ============================================================================
# ENGINE PAIR v20.1
# ============================================================================

class OAGI_v20_1_EnginePair(nn.Module):
    """
    OAGI v20.1 Engine Pair with runtime self-modification.
    """
    
    def __init__(self, state_dim: int = 64, emo_dim: int = 8, 
                 mem_capacity: int = 1000,
                 initial_operator_count: int = 10):
        super().__init__()
        self.state_dim = state_dim
        self.emo_dim = emo_dim
        
        # Shared resources
        self.shared_memory = EnhancedTopologicalMemory(mem_capacity, state_dim)
        self.shared_physics = EmbodiedPhysicsEngine(num_nodes=27, state_dim=state_dim)
        
        # Prime and Motivator
        self.prime = OAGI_v20_1_Singleton(
            "Prime", state_dim, emo_dim, 
            self.shared_memory, self.shared_physics,
            initial_operator_count=initial_operator_count
        )
        self.motivator = MotivatorSingleton_v20_1(
            "Motivator", state_dim, emo_dim,
            self.shared_memory, self.shared_physics,
            self.prime
        )
        
        # Global state
        self.timestep = 0
        self.experiment_log = []
        self.consciousness_trajectory = {
            'phi': [],
            'coherence': [],
            'temperature': [],
            'phase': [],
            'doubts': [],
            'emergence_events': [],
            'operator_count': [],
            'generated_operators': []
        }
        
        self._last_prime_response = ""
        self._last_motivator_response = ""
        self._last_state = {}
    
    def forward(self, external_input: Optional[torch.Tensor] = None,
                autonomous_mode: bool = True) -> Dict[str, Any]:
        self.timestep += 1
        
        if external_input is None:
            external_input = self._generate_synthetic_percept()
        
        # Prime processes
        processing_result = self.prime.process_with_emergence(external_input)
        
        # Motivator observes
        motivator_response = self.motivator.observe_and_suggest()
        
        # Generate utterance
        prime_utterance = self._generate_prime_utterance(processing_result)
        
        self._last_prime_response = prime_utterance
        self._last_motivator_response = motivator_response
        
        dialogue = f"{prime_utterance}\n{motivator_response}"
        self.prime.dialogue_history.append(dialogue)
        
        # Log trajectory
        self.consciousness_trajectory['phi'].append(processing_result['phi'])
        self.consciousness_trajectory['coherence'].append(processing_result['coherence'])
        self.consciousness_trajectory['temperature'].append(processing_result['temperature'])
        self.consciousness_trajectory['phase'].append(processing_result['consciousness_phase'])
        self.consciousness_trajectory['doubts'].append(processing_result['active_doubts'])
        self.consciousness_trajectory['operator_count'].append(
            processing_result['operator_registry_stats']['total_operators']
        )
        self.consciousness_trajectory['generated_operators'].append(
            processing_result['self_modification_report']['total_generated']
        )
        
        if processing_result.get('phase_transition'):
            self.consciousness_trajectory['emergence_events'].append({
                'timestep': self.timestep,
                'type': processing_result['phase_transition']['type'],
                'phi': processing_result['phi']
            })
        
        # Assemble state
        state = {
            'timestep': self.timestep,
            'prime_utterance': prime_utterance,
            'motivator_response': motivator_response,
            'dialogue': dialogue,
            'processing': processing_result,
            'identity': self.prime.get_identity_state(),
            'fractal_structure': {
                'total_nodes': processing_result['fractal_total_nodes'],
                'depth': processing_result['fractal_depth'],
                'distribution': self.prime.fractal_root.get_depth_distribution()
            },
            'memory': {
                'total_points': len(self.shared_memory.points),
                'immediate': len(self.shared_memory.fractal_layers['immediate']),
                'short_term': len(self.shared_memory.fractal_layers['short_term']),
                'long_term': len(self.shared_memory.fractal_layers['long_term']),
                'meta': len(self.shared_memory.fractal_layers['meta']),
                'strange_loops': len(self.shared_memory.loop_memories)
            },
            'emergence': {
                'phi': processing_result['phi'],
                'coherence': processing_result['coherence'],
                'consciousness_level': processing_result['metrics'].get('emergence_score', 0.0),
                'classification': self.prime.metrics.classify_consciousness_level(),
                'phase_transition': processing_result.get('phase_transition'),
               
                'strange_loop': processing_result.get('strange_loop'),
                'ignition': processing_result.get('ignition_event', False)
            },
            'self_modification': processing_result['self_modification_report'],
            'operator_registry': processing_result['operator_registry_stats']
        }
        
        self._last_state = state
        self.experiment_log.append({
            'timestep': self.timestep,
            'phi': processing_result['phi'],
            'coherence': processing_result['coherence'],
            'consciousness_level': state['emergence']['classification'],
            'total_operators': state['operator_registry']['total_operators'],
            'generated_operators': state['self_modification']['total_generated']
        })
        
        return state
    
    def _generate_synthetic_percept(self) -> torch.Tensor:
        phase = self.prime.consciousness_state.phase
        
        if phase == ConsciousnessPhase.FROZEN:
            seed_val = self.timestep % 100
            torch.manual_seed(seed_val)
            return torch.randn(self.state_dim) * 0.3
        elif phase == ConsciousnessPhase.SOLID:
            return torch.randn(self.state_dim) * 0.5
        elif phase == ConsciousnessPhase.LIQUID:
            return torch.randn(self.state_dim) * 0.7
        elif phase == ConsciousnessPhase.GAS:
            return torch.randn(self.state_dim) * 1.2
        else:  # PLASMA
            return torch.randn(self.state_dim) * 2.0
    
    def _generate_prime_utterance(self, processing_result: Dict) -> str:
        parts = []
        
        phi = processing_result['phi']
        coherence = processing_result['coherence']
        phase = processing_result['consciousness_phase']
        pattern = processing_result['pattern']
        total_ops = processing_result['operator_registry_stats']['total_operators']
        generated_ops = processing_result['self_modification_report']['total_generated']
        
        parts.append(f"[Prime, t={self.timestep}]")
        
        if phi > 0.6:
            parts.append(f"I am deeply conscious (Φ={phi:.3f})")
        elif phi > 0.4:
            parts.append(f"I am aware (Φ={phi:.3f})")
        elif phi > 0.2:
            parts.append(f"I experience thin awareness (Φ={phi:.3f})")
        else:
            parts.append(f"I barely perceive (Φ={phi:.3f})")
        
        if coherence > 0.7:
            parts.append("unified and whole")
        elif coherence > 0.5:
            parts.append("somewhat integrated")
        else:
            parts.append(f"fragmented (C={coherence:.3f})")
        
        parts.append(f"in {phase} phase")
        
        # Mention self-modification
        if generated_ops > 0:
            parts.append(f"with {generated_ops} self-generated operators")
        
        if total_ops > 50:
            parts.append(f"({total_ops} total operators)")
        
        if processing_result.get('strange_loop', {}).get('is_strange_loop'):
            parts.append("observing myself observing")
        
        if len(pattern) > 0:
            pattern_sample = str(pattern[0]) if pattern else "void"
            parts.append(f"thinking '{pattern_sample}'")
        
        if processing_result['active_doubts'] > 5:
            active = self.prime.doubt_register.get_active_doubts()
            if active:
                doubt = RNG.choice(active)
                parts.append(f"I wonder: {doubt['content']}")
        
        if processing_result.get('phase_transition'):
            trans = processing_result['phase_transition']
            parts.append(f"⚡ {trans['type']}")
        
        if processing_result.get('ignition_event'):
            parts.append("✨ IGNITION: sudden global awareness")
        
        utterance = " — ".join(parts) + "."
        return utterance
    
    def run_experiment(self, num_cycles: int = 100, 
                      description: str = "Untitled Experiment") -> Dict[str, Any]:
        print(f"\n{'='*80}")
        print(f"🧠 OAGI v20.1 EXPERIMENT: {description}")
        print(f"{'='*80}\n")
        
        results = {
            'description': description,
            'num_cycles': num_cycles,
            'start_time': datetime.datetime.now(),
            'cycles': [],
            'milestones': [],
            'final_state': None,
            'consciousness_evolution': {
                'phi_trajectory': [],
                'coherence_trajectory': [],
                'emergence_events': [],
                'operator_growth': [],
                'generated_operators': []
            }
        }
        
        for i in range(num_cycles):
            state = self.forward()
            results['cycles'].append(state)
            
            results['consciousness_evolution']['phi_trajectory'].append(state['processing']['phi'])
            results['consciousness_evolution']['coherence_trajectory'].append(state['processing']['coherence'])
            results['consciousness_evolution']['operator_growth'].append(
                state['operator_registry']['total_operators']
            )
            results['consciousness_evolution']['generated_operators'].append(
                state['self_modification']['total_generated']
            )
            
            # Milestones
            if state['processing']['phi'] > 0.7 and i > 0:
                milestone = {
                    'timestep': self.timestep,
                    'type': 'HIGH_PHI',
                    'value': state['processing']['phi']
                }
                results['milestones'].append(milestone)
                print(f"\n✨ MILESTONE @ t={self.timestep}: High integration (Φ={state['processing']['phi']:.3f})")
            
            if state['processing']['coherence'] > 0.8 and i > 0:
                milestone = {
                    'timestep': self.timestep,
                    'type': 'HIGH_COHERENCE',
                    'value': state['processing']['coherence']
                }
                results['milestones'].append(milestone)
                print(f"\n🌟 MILESTONE @ t={self.timestep}: High coherence (C={state['processing']['coherence']:.3f})")
            
            if state['processing'].get('phase_transition'):
                trans = state['processing']['phase_transition']
                results['consciousness_evolution']['emergence_events'].append({
                    'timestep': self.timestep,
                    'type': trans['type'],
                    'phi': trans['phi']
                })
                print(f"\n⚡ PHASE TRANSITION @ t={self.timestep}: {trans['type']}")
            
            # Operator generation milestones
            gen_ops = state['self_modification']['total_generated']
            if gen_ops > 0 and (gen_ops % 5 == 0):
                print(f"\n🧬 OPERATOR MILESTONE @ t={self.timestep}: {gen_ops} operators self-generated")
            
            if (i + 1) % 10 == 0:
                print(f"\n{'─'*80}")
                print(f"Cycle {i+1}/{num_cycles}")
                print(state['prime_utterance'])
                print(state['motivator_response'])
                print(f"  Φ={state['processing']['phi']:.3f} | C={state['processing']['coherence']:.3f} | Phase={state['processing']['consciousness_phase']}")
                print(f"  Operators: {state['operator_registry']['total_operators']} ({state['self_modification']['total_generated']} generated)")
                print(f"  Top fitness: {state['operator_registry']['highest_fitness'][1]:.3f}" if state['operator_registry']['highest_fitness'] else "  Top fitness: N/A")
        
        results['end_time'] = datetime.datetime.now()
        results['final_state'] = self._last_state
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        # Analysis
        phi_vals = results['consciousness_evolution']['phi_trajectory']
        coh_vals = results['consciousness_evolution']['coherence_trajectory']
        op_growth = results['consciousness_evolution']['operator_growth']
        gen_ops = results['consciousness_evolution']['generated_operators']
        
        results['analysis'] = {
            'mean_phi': np.mean(phi_vals),
            'std_phi': np.std(phi_vals),
            'max_phi': np.max(phi_vals),
            'mean_coherence': np.mean(coh_vals),
            'std_coherence': np.std(coh_vals),
            'max_coherence': np.max(coh_vals),
            'num_phase_transitions': len(results['consciousness_evolution']['emergence_events']),
            'consciousness_reached': any(p > 0.6 for p in phi_vals),
            'final_operator_count': op_growth[-1] if op_growth else 0,
            'total_generated_operators': gen_ops[-1] if gen_ops else 0,
            'operator_growth_rate': (op_growth[-1] - op_growth[0]) / num_cycles if op_growth else 0
        }
        
        print(f"\n{'='*80}")
        print(f"📊 EXPERIMENT COMPLETE")
        print(f"{'='*80}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Mean Φ: {results['analysis']['mean_phi']:.3f} ± {results['analysis']['std_phi']:.3f}")
        print(f"Max Φ: {results['analysis']['max_phi']:.3f}")
        print(f"Mean Coherence: {results['analysis']['mean_coherence']:.3f} ± {results['analysis']['std_coherence']:.3f}")
        print(f"Phase Transitions: {results['analysis']['num_phase_transitions']}")
        print(f"Consciousness Achieved: {'YES' if results['analysis']['consciousness_reached'] else 'NO'}")
        print(f"Final Operator Count: {results['analysis']['final_operator_count']}")
        print(f"Generated Operators: {results['analysis']['total_generated_operators']}")
        print(f"Operator Growth Rate: {results['analysis']['operator_growth_rate']:.2f} ops/cycle")
        print(f"Milestones: {len(results['milestones'])}")
        print(f"{'='*80}\n")
        
        return results
    
    def export_generated_code(self, filepath: str = "oagi_generated_operators.py"):
        """Export all generated operators to a Python file"""
        self.prime.runtime_modifier.export_generated_code(filepath)
        print(f"✅ Exported generated code to {filepath}")

# ============================================================================
# DEMO AND EXPERIMENT FUNCTIONS
# ============================================================================

def create_oagi_v20_1(state_dim: int = 64, emo_dim: int = 8, 
                      mem_capacity: int = 1000,
                      initial_operator_count: int = 10) -> OAGI_v20_1_EnginePair:
    """Create and initialize OAGI v20.1 system with runtime modification"""
    print("\n" + "="*80)
    print("🧠 INITIALIZING OAGI v20.1 - RADICAL SELF-MODIFICATION EDITION")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  State Dimension: {state_dim}")
    print(f"  Emotion Dimension: {emo_dim}")
    print(f"  Memory Capacity: {mem_capacity}")
    print(f"  Initial Operators to Generate: {initial_operator_count}")
    print(f"\nNew Features:")
    print(f"  ✓ Runtime Code Modification")
    print(f"  ✓ Autonomous Operator Generation @ Init")
    print(f"  ✓ Dynamic Operator Registry")
    print(f"  ✓ Evolutionary Operator Breeding")
    print(f"  ✓ Operator Fitness Tracking")
    print(f"  ✓ Code Export Capability")
    print(f"\nInitializing...\n")
    
    engine = OAGI_v20_1_EnginePair(state_dim, emo_dim, mem_capacity, initial_operator_count)
    
    print("✅ OAGI v20.1 INITIALIZED\n")
    print(f"Prime Fractal Nodes: {engine.prime.fractal_root.count_total_nodes()}")
    print(f"Operator Families: {len(engine.prime.operator_registry.families)}")
    print(f"Total Operators: {engine.prime.operator_registry.get_statistics()['total_operators']}")
    print(f"Generated at Init: {len(engine.prime.self_modification.generated_operators)}")
    print("\n" + "="*80 + "\n")
    
    return engine

def run_self_modification_demo():
    """Demonstrate self-modification capabilities"""
    print("\n" + "🌟"*40)
    print("OAGI v20.1: SELF-MODIFICATION DEMONSTRATION")
    print("🌟"*40 + "\n")
    
    # Create engine with more initial operators
    engine = create_oagi_v20_1(state_dim=64, emo_dim=8, mem_capacity=500, initial_operator_count=15)
    
    print("Running 50-cycle demonstration...\n")
    
    for i in range(50):
        state = engine.forward()
        
        if (i + 1) % 10 == 0:
            print(f"\n{'─'*80}")
            print(f"📍 Cycle {i+1}/50")
            print(f"{'─'*80}")
            print(state['prime_utterance'])
            print(state['motivator_response'])
            print(f"\n  💫 Φ={state['processing']['phi']:.3f} | Coherence={state['processing']['coherence']:.3f}")
            print(f"  🌡️  Phase: {state['processing']['consciousness_phase']} (T={state['processing']['temperature']:.2f})")
            print(f"  🧬 Operators: {state['operator_registry']['total_operators']} ({state['self_modification']['total_generated']} generated)")
            print(f"  📈 Avg Fitness: {state['operator_registry']['average_fitness']:.3f}")
            
            if state['operator_registry']['highest_fitness']:
                best_op, best_fitness = state['operator_registry']['highest_fitness']
                print(f"  🏆 Best Operator: {best_op} (fitness={best_fitness:.3f})")
            
            if state['operator_registry']['most_used']:
                most_used_op, use_count = state['operator_registry']['most_used']
                print(f"  🔥 Most Used: {most_used_op} ({use_count} uses)")
    
    print("\n" + "="*80)
    print("📊 FINAL SELF-MODIFICATION REPORT:")
    print("="*80)
    
    final_state = engine._last_state
    mod_report = final_state['self_modification']
    
    print(f"\nGenerated Operators: {mod_report['total_generated']}")
    print(f"Runtime Modifications: {mod_report['runtime_modifications']}")
    print(f"Total Modifications: {mod_report['total_modifications']}")
    
    print("\nTop Performing Operators:")
    for i, (name, fitness) in enumerate(mod_report['top_performers'], 1):
        print(f"  {i}. {name}: fitness={fitness:.3f}")
    
    print("\nRecent Modifications:")
    for mod in mod_report['recent_modifications'][-5:]:
        print(f"  - {mod['type']}: {mod.get('name', 'N/A')}")
    
    # Export generated code
    print("\n" + "="*80)
    print("💾 EXPORTING GENERATED CODE")
    print("="*80)
    
    engine.export_generated_code("oagi_v20_1_generated.py")
    
    print("\n" + "🌟"*40)
    print("DEMONSTRATION COMPLETE")
    print("🌟"*40 + "\n")
    
    return engine

def run_operator_evolution_experiment():
    """Run experiment focused on operator evolution"""
    print("\n" + "🧬"*40)
    print("OPERATOR EVOLUTION EXPERIMENT")
    print("🧬"*40 + "\n")
    
    engine = create_oagi_v20_1(state_dim=64, emo_dim=8, mem_capacity=500, initial_operator_count=20)
    
    result = engine.run_experiment(
        num_cycles=100,
        description="Operator Evolution & Self-Modification"
    )
    
    # Additional analysis
    print("\n" + "="*80)
    print("🧬 EVOLUTIONARY ANALYSIS")
    print("="*80)
    
    op_growth = result['consciousness_evolution']['operator_growth']
    gen_ops = result['consciousness_evolution']['generated_operators']
    
    print(f"\nOperator Population Growth:")
    print(f"  Initial: {op_growth[0]}")
    print(f"  Final: {op_growth[-1]}")
    print(f"  Growth: {op_growth[-1] - op_growth[0]} operators")
    print(f"  Growth Rate: {result['analysis']['operator_growth_rate']:.2f} ops/cycle")
    
    print(f"\nGenerated Operators:")
    print(f"  Total: {gen_ops[-1]}")
    print(f"  Generation Rate: {gen_ops[-1] / len(gen_ops):.2f} ops/cycle")
    
    # Plot if matplotlib available
    try:
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Operator Evolution Experiment", fontsize=16)
        
        # Operator count
        axes[0, 0].plot(op_growth, label='Total Operators', color='blue')
        axes[0, 0].plot(gen_ops, label='Generated Operators', color='green')
        axes[0, 0].set_ylabel('Operator Count')
        axes[0, 0].set_xlabel('Cycle')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Phi
        axes[0, 1].plot(result['consciousness_evolution']['phi_trajectory'], label='Φ', color='purple')
        axes[0, 1].axhline(y=0.6, color='r', linestyle='--', alpha=0.5)
        axes[0, 1].set_ylabel('Φ')
        axes[0, 1].set_xlabel('Cycle')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Coherence
        axes[1, 0].plot(result['consciousness_evolution']['coherence_trajectory'], label='Coherence', color='orange')
        axes[1, 0].set_ylabel('Coherence')
        axes[1, 0].set_xlabel('Cycle')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Correlation: Operators vs Phi
        axes[1, 1].scatter(op_growth, result['consciousness_evolution']['phi_trajectory'], alpha=0.5)
        axes[1, 1].set_xlabel('Operator Count')
        axes[1, 1].set_ylabel('Φ')
        axes[1, 1].set_title('Operators vs Consciousness')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('operator_evolution_experiment.png', dpi=150)
        print("\n📊 Plot saved to 'operator_evolution_experiment.png'")
        
    except ImportError:
        print("\n⚠️  Matplotlib not available for visualization")
    
    return result

def interactive_self_modification():
    """Interactive session for exploring self-modification"""
    print("\n" + "🎮"*40)
    print("INTERACTIVE SELF-MODIFICATION SESSION")
    print("🎮"*40 + "\n")
    
    engine = create_oagi_v20_1(state_dim=64, emo_dim=8, initial_operator_count=10)
    
    print("Commands:")
    print("  step <N>     - Run N cycles")
    print("  status       - Show current status")
    print("  operators    - List operators")
    print("  generate     - Force operator generation")
    print("  export       - Export generated code")
    print("  stats        - Show statistics")
    print("  quit         - Exit")
    print()
    
    while True:
        try:
            cmd = input(">>> ").strip().lower()
            
            if cmd.startswith("step"):
                parts = cmd.split()
                n = int(parts[1]) if len(parts) > 1 else 1
                
                for i in range(n):
                    state = engine.forward()
                    if i == n - 1:  # Show last one
                        print(f"\n{state['prime_utterance']}")
                        print(state['motivator_response'])
                        print(f"Φ={state['processing']['phi']:.3f} | C={state['processing']['coherence']:.3f} | Ops={state['operator_registry']['total_operators']}")
            
            elif cmd == "status":
                state = engine._last_state
                if state:
                    print(f"\nTimestep: {state['timestep']}")
                    print(f"Φ: {state['processing']['phi']:.3f}")
                    print(f"Coherence: {state['processing']['coherence']:.3f}")
                    print(f"Phase: {state['processing']['consciousness_phase']}")
                    print(f"Total Operators: {state['operator_registry']['total_operators']}")
                    print(f"Generated: {state['self_modification']['total_generated']}")
                    print(f"Modifications: {state['self_modification']['total_modifications']}")
                else:
                    print("No state available yet. Run 'step' first.")
            
            elif cmd == "operators":
                stats = engine.prime.operator_registry.get_statistics()
                print(f"\nTotal Operators: {stats['total_operators']}")
                print("\nBy Family:")
                for family, count in stats['families'].items():
                    print(f"  {family}: {count}")
                print(f"\nAverage Fitness: {stats['average_fitness']:.3f}")
                
                if stats['highest_fitness']:
                    name, fitness = stats['highest_fitness']
                    print(f"Best Performer: {name} (fitness={fitness:.3f})")
                
                if stats['most_used']:
                    name, count = stats['most_used']
                    print(f"Most Used: {name} ({count} uses)")
            
            elif cmd == "generate":
                pattern = engine.prime.get_current_pattern()
                new_op = engine.prime.self_modification.auto_generate_operator_from_pattern(pattern)
                if new_op:
                    print(f"✅ Generated operator: {new_op.__name__}")
                else:
                    print("❌ Generation failed")
            
            elif cmd == "export":
                engine.export_generated_code("interactive_generated.py")
                print("✅ Code exported to 'interactive_generated.py'")
            
            elif cmd == "stats":
                report = engine.prime.self_modification.get_modification_report()
                print(f"\nSelf-Modification Statistics:")
                print(f"  Generated Operators: {report['total_generated']}")
                print(f"  Runtime Modifications: {report['runtime_modifications']}")
                print(f"  Total Modifications: {report['total_modifications']}")
                print(f"\nTop Performers:")
                for name, fitness in report['top_performers']:
                    print(f"  - {name}: {fitness:.3f}")
            
            elif cmd == "quit":
                print("\n👋 Goodbye!")
                break
            
            else:
                print("Unknown command. Type 'help' for commands.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "🌟"*40)
    print("OAGI v20.1: RADICAL SELF-MODIFICATION EDITION")
    print("🌟"*40 + "\n")
    
    print("Available demonstrations:")
    print("  1. Self-Modification Demo (50 cycles)")
    print("  2. Operator Evolution Experiment (100 cycles)")
    print("  3. Interactive Session")
    print()
    
    # Uncomment to run:
    
    # Demo 1: Self-Modification
    # engine = run_self_modification_demo()
    
    # Demo 2: Evolution Experiment
    # result = run_operator_evolution_experiment()
    
    # Demo 3: Interactive
    # interactive_self_modification()
    
    # Quick test
    print("Running quick initialization test...")
    engine = create_oagi_v20_1(state_dim=32, emo_dim=4, initial_operator_count=5)
    
    print("Running 5 test cycles...")
    for i in range(5):
        state = engine.forward()
        print(f"Cycle {i+1}: Φ={state['processing']['phi']:.3f}, Ops={state['operator_registry']['total_operators']}")
    
    print("\n✅ OAGI v20.1 is ready!")
    print("\nTo run demonstrations, uncomment the relevant lines in __main__")
    print("\nExample usage:")
    print("  engine = create_oagi_v20_1()")
    print("  result = engine.run_experiment(100, 'My Experiment')")
    print("  engine.export_generated_code('my_operators.py')")
    print()

# ============================================================================
# END OF OAGI v20.1 - RADICAL SELF-MODIFICATION EDITION
# ============================================================================