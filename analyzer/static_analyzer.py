from typing import Dict, List
from slither.slither import Slither
from slither.detectors import all_detectors
from slither.detectors.abstract_detector import AbstractDetector
from slither.utils.output import Output
import inspect

class StaticAnalyzer:

    def __init__(self,source_code_path: str = "", chain: str = "ethereum") -> None:
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
            return {
                "critical": [],
                "high": [],
                "medium": [],
                "low": []
            }

        vulnerabilities = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }

        #improve: working for now but need to fix this mess

        detector_classes = [getattr(all_detectors, name) for name in dir(all_detectors) 
                          if isinstance(getattr(all_detectors, name), type) 
                          and issubclass(getattr(all_detectors, name), AbstractDetector)
                          and getattr(all_detectors, name) != AbstractDetector]

        for detector_class in detector_classes:
            try:
                sig = inspect.signature(detector_class.__init__)
                params = list(sig.parameters.keys())
                if len(params) == 4:
                    detector_instance = detector_class(self.slither.compilation_units[0], self.slither, None)
                elif len(params) == 3:
                    detector_instance = detector_class(self.slither, None)
                elif len(params) == 2:
                    detector_instance = detector_class(None)
                else:
                    print(f"Unknown constructor signature for {detector_class.__name__}: {params}")
                    continue
                results = detector_instance.detect()
                for result in results:
                    print("result here:: ",result,"\n")
                    severity = self._determine_severity(result)
                    vulnerabilities[severity].append({
                        "name": result.get("check", ""),
                        "description": result.get("description", ""),
                        "impact": result.get("impact", ""),
                        "confidence": result.get("confidence", ""),
                        "locations": result.get("locations", [])
                    })
            except Exception as e:
                print(f"Error running detector {detector_class.__name__}: {str(e)}")

        return vulnerabilities

    def _determine_severity(self, result: Dict) -> str:
        impact = result["impact"]
        confidence = result["confidence"]

        #improve: in nexts commits
        if impact == "High" and confidence == "High":
            return "critical"
        elif impact == "High" or (impact == "Medium" and confidence == "High"):
            return "high"
        elif impact == "Medium" or (impact == "Low" and confidence == "High"):
            return "medium"
        else:
            return "low"



    