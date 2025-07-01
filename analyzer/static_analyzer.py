from typing import Dict, List
from slither.slither import Slither
from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from slither.utils.output import Output
import inspect


class StaticAnalyzer:

    def __init__(self, source_code_path: str = "", chain: str = "ethereum") -> None:
        self.chain = chain
        self.source_code_path = source_code_path
        self._initialize_slither()

    def _initialize_slither(self):
        try:
            self.slither = Slither(self.source_code_path)
        except Exception as e:
            print(f"Failed to initialize Slither: {str(e)}")
            self.slither = None

    def analyze_vulnerabilities(self) -> Dict[str, List[Dict]]:
        if not self.slither:
            print("Slither not initialized")
            return {"critical": [], "high": [], "medium": [], "low": []}

        vulnerabilities = {"critical": [], "high": [], "medium": [], "low": []}

        # improve: working for now but need to fix this mess

        detector_classes = [
            getattr(all_detectors, name)
            for name in dir(all_detectors)
            if isinstance(getattr(all_detectors, name), type)
            and issubclass(getattr(all_detectors, name), AbstractDetector)
            and getattr(all_detectors, name) != AbstractDetector
        ]

        for detector_class in detector_classes:
            try:
                sig = inspect.signature(detector_class.__init__)
                params = list(sig.parameters.keys())
                if len(params) == 4:
                    detector_instance = detector_class(
                        self.slither.compilation_units[0], self.slither, None
                    )
                elif len(params) == 3:
                    detector_instance = detector_class(self.slither, None)
                elif len(params) == 2:
                    detector_instance = detector_class(None)
                else:
                    print(
                        f"Unknown constructor signature for {detector_class.__name__}: {params}"
                    )
                    continue
                results = detector_instance.detect()
                for result in results:
                    severity = self._determine_severity(result)
                    vulnerabilities[severity].append(
                        {
                            "name": result.get("check", ""),
                            "description": result.get("description", ""),
                            "impact": result.get("impact", ""),
                            "confidence": result.get("confidence", ""),
                            "locations": result.get("locations", []),
                        }
                    )
            except Exception as e:
                print(f"Error running detector {detector_class.__name__}: {str(e)}")

        return vulnerabilities

    def _determine_severity(self, result: Dict) -> str:
        impact = result["impact"]
        confidence = result["confidence"]

        # improve: in nexts commits
        if impact == "High" and confidence == "High":
            return "critical"
        elif impact == "High" or (impact == "Medium" and confidence == "High"):
            return "high"
        elif impact == "Medium" or (impact == "Low" and confidence == "High"):
            return "medium"
        else:
            return "low"

    def analyze_gas_optimization(self) -> List[Dict]:

        if not self.slither:
            print("slither not initilaized ")

        optimizations = []
        for contract in self.slither.contracts:

            # self._analyze_storage_usage(contract, optimizations)
            # self._analyze_loops(contract, optimizations)
            self._analyze_function_visibility(contract,optimizations)

        return optimizations

    def _analyze_loops(self, contract, optimizations: List[Dict]):
        for function in contract.functions:
            nodes = function.nodes
            i = 0
            while i < len(nodes):
                node = nodes[i]
                if "IFLOOP" in str(node.type):
                    loop_body_nodes = []
                    i += 1
                    while i < len(nodes) and "ENDLOOP" not in str(nodes[i].type):
                        loop_body_nodes.append(nodes[i])
                        i += 1
                    storage_access = False
                    for body_node in loop_body_nodes:
                        if hasattr(body_node, "variables"):
                            for var in body_node.variables:
                                if getattr(var, "is_storage", False):
                                    storage_access = True
                                    break
                        if (
                            hasattr(body_node, "expression")
                            and body_node.expression is not None
                        ):
                            for state_var in contract.state_variables:
                                if state_var.name in str(body_node.expression):
                                    storage_access = True
                                    break
                        if storage_access:
                            break
                    if storage_access:
                        optimizations.append(
                            {
                                "type": "loop",
                                "description": f"Consider caching storage variable in memory for loop in {function.name}",
                                "impact": "High",
                                "location": node.source_mapping,
                            }
                        )
                else:
                    i += 1

    def _analyze_storage_usage(self, contract, optimizations: List[Dict]):
        seen_packed = set()

        # improve:  i think this ocde is redundant and hard coded so might need some refactoring for it.
        for variable in contract.state_variables:
            try:
                if getattr(variable, "is_constant", False) or getattr(
                    variable, "is_immutable", False
                ):
                    continue

                if hasattr(variable.type, "is_dynamic") and variable.type.is_dynamic:
                    optimizations.append(
                        {
                            "type": "storage",
                            "description": f"Review if dynamic type {variable.type} for {variable.name} is necessary. Use fixed-size types if possible.",
                            "impact": "Medium",
                            "location": variable.source_mapping,
                        }
                    )

                if getattr(variable, "visibility", "") == "public":
                    optimizations.append(
                        {
                            "type": "visibility",
                            "description": f"Variable {variable.name} is public. Consider internal/private if external access is unnecessary.",
                            "impact": "Low",
                            "location": variable.source_mapping,
                        }
                    )

                references = getattr(variable, "references", [])
                if len(references) == 0:
                    optimizations.append(
                        {
                            "type": "unused",
                            "description": f"Variable {variable.name} is never used. Remove to save gas.",
                            "impact": "Low",
                            "location": variable.source_mapping,
                        }
                    )

                write_refs = [
                    ref for ref in references if getattr(ref, "is_write", False)
                ]
                if len(write_refs) == 1:
                    optimizations.append(
                        {
                            "type": "immutability",
                            "description": f"Variable {variable.name} is written only once. Consider making it immutable or constant.",
                            "impact": "Medium",
                            "location": variable.source_mapping,
                        }
                    )

            except Exception as e:
                print(
                    f"[Warning] Skipping variable {getattr(variable, 'name', 'unknown')} due to error: {str(e)}"
                )

        try:
            value_vars = [
                v
                for v in contract.state_variables
                if hasattr(v, "type")
                and getattr(v.type, "is_value_type", False)
                and not getattr(v, "is_constant", False)
            ]

            # code suggestion by gpt: might cause errors
            for i, var1 in enumerate(value_vars):
                for var2 in value_vars[i + 1 :]:
                    try:
                        name_pair = tuple(sorted([var1.name, var2.name]))
                        if name_pair in seen_packed:
                            continue
                        total_size = getattr(var1.type, "size", 0) + getattr(
                            var2.type, "size", 0
                        )
                        if total_size <= 32:
                            optimizations.append(
                                {
                                    "type": "storage_packing",
                                    "description": f"Consider packing {var1.name} and {var2.name} in the same storage slot.",
                                    "impact": "High",
                                    "location": var1.source_mapping,
                                }
                            )
                            seen_packed.add(name_pair)
                    except Exception as e:
                        print(
                            f"[Storage Packing Warning] Failed on vars {var1.name}, {var2.name}: {e}"
                        )
        except Exception as e:
            print(f"[Critical] Storage packing analysis failed: {e}")


    def _analyze_function_visibility(self, contract, optimizations: List[Dict]):

        internal_calls = set()
        for function in contract.functions:
            for call in function.internal_calls:
                if hasattr(call, 'name'):
                    internal_calls.add(call.name)
        
        for function in contract.functions:

    #          print("All the functions in contract.functions --> ",function, " is ",function.visibility)
    #          print("call name:",function.internal_calls)

            if (function.is_constructor or function.is_fallback or function.is_receive): # we can skip these for now
                continue
            
            if function.visibility == "public":
                is_called_internally = (
                    function.name in internal_calls or
                    any(function.name in [call.name for call in other_func.internal_calls if hasattr(call, 'name')] 
                        for other_func in contract.functions if other_func != function)
                )
                
                if not is_called_internally and not getattr(function, 'is_override', False):
                    optimizations.append({
                        "type": "visibility",
                        "description": f"Consider changing {function.name} visibility to external",
                        "impact": "Low",
                        "location": function.source_mapping
                    })
            
            elif function.visibility == "internal":
                # Check if function is only used within current contract
                is_used_by_derived = any(
                    function.name in [f.name for f in derived.functions] 
                    for derived in contract.derived_contracts
                )
                
                if not is_used_by_derived and not getattr(function, 'is_override', False):
                    optimizations.append({
                        "type": "visibility",
                        "description": f"Consider changing {function.name} visibility to private",
                        "impact": "Low",
                        "location": function.source_mapping
                    })
            
            if function.visibility in ["private", "internal"]:
                is_function_used = (
                    function.name in internal_calls or
                    any(call.name == function.name for other_func in contract.functions 
                        for call in other_func.internal_calls if hasattr(call, 'name') and other_func != function)
                )
                
                if not is_function_used and not function.is_override:
                    optimizations.append({
                        "type": "visibility",
                        "description": f"Function {function.name} appears unused and could be removed",
                        "impact": "Medium",
                        "location": function.source_mapping
                    })
            
           