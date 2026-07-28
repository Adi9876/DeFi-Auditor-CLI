import argparse
import asyncio
import json
from typing import List
import os
from analyzer.static_analyzer import StaticAnalyzer


from config.config import *
from tools.llm_analyzer import analyze_access_control
from tools.report_generator import finalize_report, generate_report_section


class DefiAuditor:

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def _get_contract_files(self, path: str) -> List[str]:
        contract_files = []

        if os.path.isfile(path):
            if path.endswith((".sol", ".vy")):
                contract_files.append(path)
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith((".sol", ".vy")):
                        contract_files.append(os.path.join(root, file))

        return contract_files

    async def audit_contract_files(
        self, paths: List[str], compiler_version: str = "", output_format: str = "pdf"
    ) -> str:
        try:
            all_contract_files = []
            for path in paths:
                all_contract_files.extend(self._get_contract_files(path))

            if not all_contract_files:
                raise print("No contract files found in the specified paths")

            print(f"Found {len(all_contract_files)} contract files to analyze")

            contract_analyses = []
            for contract_file in all_contract_files:
                print(f"Analyzing {contract_file}...")

                with open(contract_file, "r") as f:
                    source_code = f.read()

                self.static_analyzer = StaticAnalyzer(
                    source_code, compiler_version, self.chain
                )
                vulnerabilities = self.static_analyzer.analyze_vulnerabilities()
                # optimizations = self.static_analyzer.analyze_gas_optimization()


        except:
            print("error")

##############
# Testing Out Functions Here 
    async def full_audit(self, paths: List[str], output_format: str = "html"):
        all_contract_files = []
        for path in paths:
            all_contract_files.extend(self._get_contract_files(path))

        if not all_contract_files:
            print("No contract files found in the specified paths")
            return

        from tools.llm_analyzer import analyze_access_control
        from tools.report_generator import finalize_report, generate_report_section
        from llm.severity_classifier import classify_severity

        for contract_file in all_contract_files:
            print(f"Analyzing {contract_file}...")

            with open(contract_file, "r") as f:
                source_code = f.read()

            self.static_analyzer = StaticAnalyzer(
                contract_file, self.chain
            )
            
            print("Running static analysis...")
            vulnerabilities = self.static_analyzer.analyze_vulnerabilities()
            optimizations = self.static_analyzer.analyze_gas_optimization()

            vuln_notes = []
            for severity, vulns in vulnerabilities.items():
                for vuln in vulns:
                    actual_severity = classify_severity(vuln.get('description', ''))
                    vuln_notes.append(f"- **[{actual_severity}]** {vuln.get('name', 'Issue')}: {vuln.get('description', '')}")

            opt_notes = "\n".join([f"- {opt.get('description', '')}" for opt in optimizations])

            print("Running LLM analysis...")
            try:
                llm_analysis = analyze_access_control(source_code, opt_notes)
            except Exception as e:
                print(f"LLM analysis failed: {str(e)}")
                llm_analysis = f"Error during LLM analysis: {str(e)}"

            generate_report_section(f"📄 File: {contract_file}", "**Analysis Results**")

            if vuln_notes:
                generate_report_section("🚨 Vulnerabilities", "\n".join(vuln_notes))
            else:
                generate_report_section("🚨 Vulnerabilities", "No vulnerabilities detected by static analyzer.")

            if opt_notes:
                generate_report_section("🔧 Gas Optimizations", opt_notes)

            generate_report_section("🤖 LLM Access Control & Security Analysis", llm_analysis)

        # Finalize report 
        finalize_report(output_format)
        print(f"Audit completed! Report saved as audit_report.{output_format}")


    # async def test_file_fetch(
    #     self,
    #     paths: str,
    # ) -> List[str]:

    #     try:
    #         all_contract_files = []
    #         for path in paths:
    #             all_contract_files.extend(self._get_contract_files(path))

    #         if not all_contract_files:
    #             print("No contract files found in the specified paths")

    #         print(f"Found {len(all_contract_files)} contract files to analyze")
    #         return all_contract_files
    #     except:
    #         print(f"Error here")

    # async def test_analyzer(
    #     self,
    #     paths: str,
    # ) -> List[str]:

    #     try:
    #         all_contract_files = []
    #         for path in paths:
    #             all_contract_files.extend(self._get_contract_files(path))

    #         if not all_contract_files:
    #             print("No contract files found in the specified paths")

    #         print(f"Found {len(all_contract_files)} contract files to analyze")

    #         contract_analyses = []
    #         for contract_file in all_contract_files:
    #             print(f"Analyzing {contract_file}...")

    #             with open(contract_file, "r") as f:
    #                 source_code = f.read()
    #                 self.static_analyzer = StaticAnalyzer(contract_file, self.chain)
    #                 vulns = self.static_analyzer.analyze_vulnerabilities()
    #                 print(f"Vulnerabilities for {contract_file}:\n{vulns}")
    #                 contract_analyses.append({contract_file: vulns})

    #         return contract_analyses
    #     except Exception as e:
    #         print(f"Error here", str(e))

    # async def test_gas_optimizer(self, paths: List[str]) -> None:
    #     try:
    #         all_contract_files = []
    #         for path in paths:
    #             all_contract_files.extend(self._get_contract_files(path))

    #         if not all_contract_files:
    #             print("No contract files found in the specified paths")
    #             return

    #         print(f"Found {len(all_contract_files)} contract files for gas optimization analysis")

    #         for contract_file in all_contract_files:
    #             print(f"Running gas optimization analysis on {contract_file}...")

    #             analyzer = StaticAnalyzer(contract_file, self.chain)
    #             optimizations = analyzer.analyze_gas_optimization()

    #             print(f"Gas optimization opportunities for {contract_file}:")
    #             for opt in optimizations:
    #                 print(f"- {opt}")
    #     except Exception as e:
    #         print(f"Error during gas optimization analysis: {str(e)}")


##################
# Main function

async def main():
    parser = argparse.ArgumentParser(description="DeFi Smart Contract Auditor")

    parser.add_argument(
        "--files",
        nargs="+",
        required=True,
        help="Paths to smart contract files or directories to audit",
    )

    parser.add_argument(
        "--chain",
        default="ethereum",
        choices=["ethereum", "bsc", "avalanche"],
        help="chain",
    )

    args = parser.parse_args()

    auditor = DefiAuditor(args.chain)
    # contract_files = await auditor.test_file_fetch(args.files)
    # for i in contract_files:
    #     print("we have", i)

    # await auditor.test_analyzer(args.files)

    # await auditor.test_gas_optimizer(args.files)

    await auditor.full_audit(args.files, output_format="html")

    await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
