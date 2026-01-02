"""
Main Application for Resource Scheduling & Capacity Analysis System

This is the primary entry point that orchestrates:
- Data generation
- Scheduling execution
- Capacity analysis
- Results reporting
"""

import json
from datetime import datetime
from typing import Dict, Optional, List, Any

from src.core.models import Schedule, SkillType
from src.core.generator import DataGenerator
from src.core.scheduler import schedule_projects, ScheduleAnalyzer
from src.core.analyzer import CapacityAnalyzer


class SchedulingApplication:
    """Main application class for the scheduling system"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize the scheduling application.
        
        Args:
            seed: Random seed for reproducibility
        """
        self.seed = seed
        self.generator = DataGenerator(seed=seed)
        self.schedule: Optional[Schedule] = None
        self.scheduling_results: Optional[Dict[str, Any]] = None
        self.capacity_report: Optional[Dict[str, Any]] = None
    
    def setup_scenario(
        self,
        scenario_name: str = 'balanced',
        num_employees: int = 100,
        num_projects: int = 100
    ) -> Dict[str, Any]:
        """
        Set up a scheduling scenario.
        
        Args:
            scenario_name: Name of the scenario
            num_employees: Number of employees
            num_projects: Number of projects
        
        Returns:
            Scenario metadata
        """
        print(f"\n{'='*60}")
        print(f"Setting up scenario: {scenario_name}")
        print(f"{'='*60}")
        
        self.schedule, metadata = self.generator.generate_scenario(
            scenario_name,
            num_employees=num_employees,
            num_projects=num_projects
        )
        
        print(f"✓ Generated {len(self.schedule.employees)} employees")
        print(f"✓ Generated {len(self.schedule.projects)} projects")
        
        return metadata
    
    def run_scheduling(self, strategy: str = 'greedy') -> Dict[str, Any]:
        """
        Execute the scheduling algorithm.
        
        Args:
            strategy: Scheduling strategy ('greedy' or 'optimized')
        
        Returns:
            Scheduling results
        """
        if self.schedule is None:
            raise ValueError("No schedule set up. Call setup_scenario() first.")
        
        print(f"\n{'='*60}")
        print(f"Running {strategy} scheduling algorithm...")
        print(f"{'='*60}")
        
        self.scheduling_results = schedule_projects(
            self.schedule,
            strategy=strategy,
            balance_workload=True,
            minimize_overtime=True
        )
        
        print(f"\n✓ Scheduling complete!")
        print(f"  - Scheduled projects: {self.scheduling_results['scheduled_projects']}")
        print(f"  - Failed projects: {len(self.scheduling_results['failed_projects'])}")
        
        if self.scheduling_results['failed_projects']:
            print(f"\n⚠ Warning: {len(self.scheduling_results['failed_projects'])} projects could not be fully staffed")
            for failed in self.scheduling_results['failed_projects'][:3]:  # Show first 3
                print(f"  - {failed['name']}: Missing {', '.join(failed['missing_skills'])}")
        
        return self.scheduling_results
    
    def run_capacity_analysis(self, analysis_period_days: int = 365) -> Dict[str, Any]:
        """
        Perform capacity analysis.
        
        Args:
            analysis_period_days: Analysis period in days
        
        Returns:
            Capacity analysis report
        """
        if self.schedule is None:
            raise ValueError("No schedule set up. Call setup_scenario() first.")
        
        print(f"\n{'='*60}")
        print(f"Running capacity analysis...")
        print(f"{'='*60}")
        
        analyzer = CapacityAnalyzer(self.schedule, analysis_period_days)
        self.capacity_report = analyzer.generate_capacity_report()
        
        # Print summary
        summary = self.capacity_report['summary']
        print(f"\n✓ Analysis complete!")
        print(f"  - Total employees: {summary['total_employees']}")
        print(f"  - Active employees: {summary['active_employees']}")
        print(f"  - Average utilization: {summary['average_utilization']:.1f}%")
        print(f"  - Total cost: {summary['total_cost']:.2f} units")
        print(f"  - Overtime cost: {summary['overtime_cost_percentage']:.1f}%")
        
        return self.capacity_report
    
    def generate_recommendations(self) -> List[str]:
        """
        Generate actionable recommendations.
        
        Returns:
            List of recommendations
        """
        if self.schedule is None:
            raise ValueError("No schedule set up.")
        
        print(f"\n{'='*60}")
        print(f"Generating recommendations...")
        print(f"{'='*60}")
        
        recommendations = ScheduleAnalyzer.generate_recommendations(self.schedule)
        
        print(f"\n✓ Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec}")
        
        return recommendations
    
    def print_summary_report(self) -> None:
        """Print a comprehensive summary report"""
        if self.schedule is None:
            print("No schedule available. Run setup_scenario() first.")
            return
        
        print(f"\n{'='*60}")
        print(f"SCHEDULING SYSTEM SUMMARY REPORT")
        print(f"{'='*60}")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Schedule validation
        validation = self.schedule.validate_schedule()
        print(f"\n--- Schedule Validation ---")
        print(f"Valid: {'✓ Yes' if validation['valid'] else '✗ No'}")
        print(f"Total employees: {validation['stats']['total_employees']}")
        print(f"Total projects: {validation['stats']['total_projects']}")
        print(f"Fully staffed projects: {validation['stats']['fully_staffed_projects']}")
        print(f"Total assignments: {validation['stats']['total_assignments']}")
        
        if validation['errors']:
            print(f"\nErrors:")
            for error in validation['errors']:
                print(f"  ✗ {error}")
        
        if validation['warnings']:
            print(f"\nWarnings:")
            for warning in validation['warnings']:
                print(f"  ⚠ {warning}")
        
        # Scheduling results
        if self.scheduling_results:
            print(f"\n--- Scheduling Results ---")
            stats = self.scheduling_results['statistics']
            print(f"Total cost: {stats['total_cost']:.2f} units")
            print(f"Regular hours: {stats['total_regular_hours']:.1f}")
            print(f"Overtime hours: {stats['total_overtime_hours']:.1f}")
            print(f"Employees with overtime: {stats['employees_with_overtime']}")
            print(f"Average utilization: {stats['average_utilization']:.1f} hours/employee")
        
        # Capacity analysis
        if self.capacity_report:
            print(f"\n--- Capacity Analysis ---")
            summary = self.capacity_report['summary']
            workforce = self.capacity_report['workforce_sizing']
            
            print(f"Average utilization: {summary['average_utilization']:.1f}%")
            print(f"Idle employees: {summary['idle_employees']}")
            print(f"Overtime cost percentage: {summary['overtime_cost_percentage']:.1f}%")
            
            print(f"\n--- Workforce Sizing Recommendation ---")
            print(f"Current headcount: {workforce['current_headcount']}")
            print(f"Recommended headcount: {workforce['recommended_headcount']}")
            print(f"Confidence: {workforce['confidence_level']}")
            print(f"\nReasoning: {workforce['reasoning']}")
            
            if workforce['expected_cost_impact'] != 0:
                impact = "savings" if workforce['expected_cost_impact'] < 0 else "increase"
                print(f"Expected cost {impact}: {abs(workforce['expected_cost_impact']):.2f} units")
        
        print(f"\n{'='*60}\n")
    
    def save_results(self, output_dir: str = ".") -> None:
        """
        Save all results to JSON files.
        
        Args:
            output_dir: Output directory
        """
        import os
        
        if self.schedule is None:
            print("No schedule to save.")
            return
        
        print(f"\n{'='*60}")
        print(f"Saving results to {output_dir}...")
        print(f"{'='*60}")
        
        # Save schedule
        schedule_file = os.path.join(output_dir, "schedule.json")
        self.schedule.save_to_file(schedule_file)
        print(f"✓ Saved schedule to {schedule_file}")
        
        # Save scheduling results
        if self.scheduling_results:
            results_file = os.path.join(output_dir, "scheduling_results.json")
            with open(results_file, 'w') as f:
                json.dump(self.scheduling_results, f, indent=2)
            print(f"✓ Saved scheduling results to {results_file}")
        
        # Save capacity report
        if self.capacity_report:
            report_file = os.path.join(output_dir, "capacity_report.json")
            with open(report_file, 'w') as f:
                json.dump(self.capacity_report, f, indent=2)
            print(f"✓ Saved capacity report to {report_file}")
        
        print(f"\n✓ All results saved successfully!")
    
    def run_complete_analysis(
        self,
        scenario_name: str = 'balanced',
        num_employees: int = 100,
        num_projects: int = 100,
        strategy: str = 'greedy'
    ) -> Dict[str, Any]:
        """
        Run complete end-to-end analysis.
        
        Args:
            scenario_name: Scenario to run
            num_employees: Number of employees
            num_projects: Number of projects
            strategy: Scheduling strategy
        
        Returns:
            Complete results dictionary
        """
        # Setup
        metadata = self.setup_scenario(scenario_name, num_employees, num_projects)
        
        # Schedule
        scheduling_results = self.run_scheduling(strategy)
        
        # Analyze
        capacity_report = self.run_capacity_analysis()
        
        # Recommendations
        recommendations = self.generate_recommendations()
        
        # Print summary
        self.print_summary_report()
        
        # Save results
        self.save_results()
        
        return {
            'metadata': metadata,
            'scheduling_results': scheduling_results,
            'capacity_report': capacity_report,
            'recommendations': recommendations
        }


def main():
    """Main entry point for the application"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Resource Scheduling & Capacity Analysis System              ║
    ║  Advanced Workforce Optimization for Media Production        ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Create application
    app = SchedulingApplication(seed=42)
    
    # Run complete analysis
    results = app.run_complete_analysis(
        scenario_name='balanced',
        num_employees=100,
        num_projects=100,
        strategy='greedy'
    )
    
    print("\n✓ Analysis complete! Check the generated JSON files for detailed results.")
    print("\nNext steps:")
    print("  1. Review the capacity_report.json for detailed analytics")
    print("  2. Run 'python api_server.py' to start the web dashboard")
    print("  3. Open http://127.0.0.1:5000 in your browser")
    print("  4. Experiment with different scenarios")
    
    return results


if __name__ == "__main__":
    main()
