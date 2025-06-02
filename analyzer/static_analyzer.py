from slither.slither import Slither


class StaticAnalyzer:

    def __init__(self,source_code: str = "", chain: str = "ethereum") -> None:
        self.chain = chain
        self.source_code = source_code
    
        self._initialize_slither()
    

    def _initialize_slither(self):
        try:
            self.slither = Slither(self.source_code)
        except Exception as e:
            print(f"Failed to initialize Slither: {str(e)}")
    

