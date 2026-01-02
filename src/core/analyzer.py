from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

from .models import Employee, Project, Schedule, SkillType


@dataclass
class UtilizationMetrics:
    employee_id: int
    employee_name: str
    total_hours: float
    regular_hours: float
    overtime_hours: float
    utilization_rate: float
    overtime_percentage: float
    num_assignments: int
    total_cost: float


@dataclass
class TeamMetrics:
    total_employees: int
    active_employees: int
    idle_employees: int
    total_hours_worked: float
    total_regular_hours: float
    total_overtime_hours: float
    average_utilization: float
    utilization_std_dev: float
    total_cost: float
    average_cost_per_employee: float


@dataclass
class CostAnalysis:
    total_cost: float
    regular_cost: float
    overtime_cost: float
    overtime_cost_percentage: float
    cost_per_project: float
    cost_per_hour: float


@dataclass
class WorkforceSizingRecommendation:
    current_headcount: int
    recommended_headcount: int
    reasoning: str
    expected_cost_impact: float
    expected_overtime_reduction: float
    confidence_level: str


class CapacityAnalyzer:
    
    def __init__(self, schedule: Schedule, analysis_period_days: int = 365):
        self.schedule = schedule
        self.analysis_period_days = analysis_period_days
        self.hours_per_employee_per_period = analysis_period_days * 8
    
    def calculate_employee_utilization(self, employee: Employee) -> UtilizationMetrics:
        total_hours = employee.regular_hours_worked + employee.overtime_hours_worked
        utilization_rate = employee.get_utilization_rate(self.hours_per_employee_per_period)
        overtime_pct = employee.get_overtime_percentage()
        
        return UtilizationMetrics(
            employee_id=employee.id,
            employee_name=employee.name,
            total_hours=total_hours,
            regular_hours=employee.regular_hours_worked,
            overtime_hours=employee.overtime_hours_worked,
            utilization_rate=utilization_rate,
            overtime_percentage=overtime_pct,
            num_assignments=len(employee.assignments),
            total_cost=employee.get_total_cost()
        )
    
    def calculate_team_utilization(self) -> TeamMetrics:
        if not self.schedule.employees:
            return TeamMetrics(
                total_employees=0,
                active_employees=0,
                idle_employees=0,
                total_hours_worked=0,
                total_regular_hours=0,
                total_overtime_hours=0,
                average_utilization=0,
                utilization_std_dev=0,
                total_cost=0,
                average_cost_per_employee=0
            )
        
        total_employees = len(self.schedule.employees)
        active_employees = len([e for e in self.schedule.employees if e.assignments])
        idle_employees = total_employees - active_employees
        
        total_regular = sum(e.regular_hours_worked for e in self.schedule.employees)
        total_overtime = sum(e.overtime_hours_worked for e in self.schedule.employees)
        total_hours = total_regular + total_overtime
        
        utilization_rates = [
            e.get_utilization_rate(self.hours_per_employee_per_period)
            for e in self.schedule.employees
        ]
        
        avg_utilization = statistics.mean(utilization_rates) if utilization_rates else 0
        std_dev = statistics.stdev(utilization_rates) if len(utilization_rates) > 1 else 0
        
        total_cost = self.schedule.get_total_cost()
        avg_cost = total_cost / total_employees if total_employees > 0 else 0
        
        return TeamMetrics(
            total_employees=total_employees,
            active_employees=active_employees,
            idle_employees=idle_employees,
            total_hours_worked=total_hours,
            total_regular_hours=total_regular,
            total_overtime_hours=total_overtime,
            average_utilization=avg_utilization,
            utilization_std_dev=std_dev,
            total_cost=total_cost,
            average_cost_per_employee=avg_cost
        )
    
    def identify_underutilized_employees(self, threshold: float = 50.0) -> List[UtilizationMetrics]:
        underutilized = []
        
        for employee in self.schedule.employees:
            metrics = self.calculate_employee_utilization(employee)
            if metrics.utilization_rate < threshold:
                underutilized.append(metrics)
        
        underutilized.sort(key=lambda m: m.utilization_rate)
        
        return underutilized
    
    def identify_overworked_employees(self, overtime_threshold: float = 20.0) -> List[UtilizationMetrics]:
        overworked = []
        
        for employee in self.schedule.employees:
            metrics = self.calculate_employee_utilization(employee)
            if metrics.overtime_percentage > overtime_threshold:
                overworked.append(metrics)
        
        overworked.sort(key=lambda m: m.overtime_percentage, reverse=True)
        
        return overworked
    
    def analyze_costs(self) -> CostAnalysis:
        total_regular = sum(e.regular_hours_worked for e in self.schedule.employees)
        total_overtime = sum(e.overtime_hours_worked for e in self.schedule.employees)
        
        regular_cost = total_regular * Employee.REGULAR_RATE
        overtime_cost = total_overtime * Employee.OVERTIME_RATE
        total_cost = regular_cost + overtime_cost
        
        overtime_cost_pct = (overtime_cost / total_cost * 100) if total_cost > 0 else 0
        
        num_projects = len([p for p in self.schedule.projects if p.is_fully_staffed()])
        cost_per_project = total_cost / num_projects if num_projects > 0 else 0
        
        total_hours = total_regular + total_overtime
        cost_per_hour = total_cost / total_hours if total_hours > 0 else 0
        
        return CostAnalysis(
            total_cost=total_cost,
            regular_cost=regular_cost,
            overtime_cost=overtime_cost,
            overtime_cost_percentage=overtime_cost_pct,
            cost_per_project=cost_per_project,
            cost_per_hour=cost_per_hour
        )
    
    def compare_overtime_vs_hiring(self, additional_employees: int = 1) -> Dict[str, Any]:
        current_cost_analysis = self.analyze_costs()
        current_total_cost = current_cost_analysis.total_cost
        current_overtime_cost = current_cost_analysis.overtime_cost
        
        total_overtime_hours = sum(e.overtime_hours_worked for e in self.schedule.employees)
        
        overtime_hours_eliminated = min(
            total_overtime_hours,
            additional_employees * self.hours_per_employee_per_period
        )
        
        overtime_savings = overtime_hours_eliminated * (Employee.OVERTIME_RATE - Employee.REGULAR_RATE)
        
        hiring_cost = additional_employees * self.hours_per_employee_per_period * Employee.REGULAR_RATE
        
        net_cost_difference = hiring_cost - overtime_savings
        
        if overtime_savings > 0:
            breakeven_employees = current_overtime_cost / (self.hours_per_employee_per_period * Employee.REGULAR_RATE)
        else:
            breakeven_employees = float('inf')
        
        return {
            'current_scenario': {
                'total_cost': current_total_cost,
                'overtime_cost': current_overtime_cost,
                'overtime_hours': total_overtime_hours
            },
            'hiring_scenario': {
                'additional_employees': additional_employees,
                'hiring_cost': hiring_cost,
                'overtime_eliminated_hours': overtime_hours_eliminated,
                'overtime_savings': overtime_savings,
                'net_cost_difference': net_cost_difference,
                'total_cost': current_total_cost + net_cost_difference
            },
            'recommendation': 'hire' if net_cost_difference < 0 else 'overtime',
            'breakeven_employees': breakeven_employees,
            'cost_benefit_ratio': overtime_savings / hiring_cost if hiring_cost > 0 else 0
        }
    
    def recommend_workforce_size(self) -> WorkforceSizingRecommendation:
        current_headcount = len(self.schedule.employees)
        team_metrics = self.calculate_team_utilization()
        cost_analysis = self.analyze_costs()
        
        total_hours_needed = team_metrics.total_hours_worked
        ideal_headcount_by_hours = total_hours_needed / self.hours_per_employee_per_period
        
        if team_metrics.total_overtime_hours > 0:
            overtime_pct = (team_metrics.total_overtime_hours / team_metrics.total_hours_worked) * 100
            
            if overtime_pct > 15:
                additional_needed = team_metrics.total_overtime_hours / self.hours_per_employee_per_period
                recommended = int(current_headcount + additional_needed + 0.5)
                
                comparison = self.compare_overtime_vs_hiring(int(additional_needed + 0.5))
                
                return WorkforceSizingRecommendation(
                    current_headcount=current_headcount,
                    recommended_headcount=recommended,
                    reasoning=f"High overtime ({overtime_pct:.1f}%) detected. "
                              f"Hiring {recommended - current_headcount} additional employees "
                              f"would reduce overtime and potentially lower costs.",
                    expected_cost_impact=comparison['hiring_scenario']['net_cost_difference'],
                    expected_overtime_reduction=comparison['hiring_scenario']['overtime_eliminated_hours'],
                    confidence_level='high' if overtime_pct > 20 else 'medium'
                )
        
        if team_metrics.average_utilization < 60:
            optimal_headcount = int(ideal_headcount_by_hours + 0.5)
            reduction = current_headcount - optimal_headcount
            
            if reduction > 0:
                cost_savings = reduction * team_metrics.average_cost_per_employee
                
                return WorkforceSizingRecommendation(
                    current_headcount=current_headcount,
                    recommended_headcount=optimal_headcount,
                    reasoning=f"Low average utilization ({team_metrics.average_utilization:.1f}%). "
                              f"Workforce could be reduced by {reduction} employees.",
                    expected_cost_impact=-cost_savings,
                    expected_overtime_reduction=0,
                    confidence_level='medium'
                )
        
        return WorkforceSizingRecommendation(
            current_headcount=current_headcount,
            recommended_headcount=current_headcount,
            reasoning=f"Current workforce size is appropriate. "
                      f"Average utilization is {team_metrics.average_utilization:.1f}% "
                      f"with {cost_analysis.overtime_cost_percentage:.1f}% overtime costs.",
            expected_cost_impact=0,
            expected_overtime_reduction=0,
            confidence_level='high'
        )
    
    def generate_capacity_report(self) -> Dict[str, Any]:
        team_metrics = self.calculate_team_utilization()
        cost_analysis = self.analyze_costs()
        workforce_recommendation = self.recommend_workforce_size()
        
        all_employee_metrics = [
            self.calculate_employee_utilization(emp)
            for emp in self.schedule.employees
        ]
        all_employee_metrics.sort(key=lambda m: m.utilization_rate, reverse=True)
        
        top_utilized = all_employee_metrics[:5] if len(all_employee_metrics) >= 5 else all_employee_metrics
        bottom_utilized = all_employee_metrics[-5:] if len(all_employee_metrics) >= 5 else []
        
        underutilized = self.identify_underutilized_employees()
        overworked = self.identify_overworked_employees()
        
        overtime_comparison = self.compare_overtime_vs_hiring()
        
        return {
            'summary': {
                'analysis_period_days': self.analysis_period_days,
                'total_employees': team_metrics.total_employees,
                'active_employees': team_metrics.active_employees,
                'idle_employees': team_metrics.idle_employees,
                'average_utilization': team_metrics.average_utilization,
                'total_cost': cost_analysis.total_cost,
                'overtime_cost_percentage': cost_analysis.overtime_cost_percentage
            },
            'team_metrics': {
                'total_hours_worked': team_metrics.total_hours_worked,
                'regular_hours': team_metrics.total_regular_hours,
                'overtime_hours': team_metrics.total_overtime_hours,
                'utilization_std_dev': team_metrics.utilization_std_dev,
                'average_cost_per_employee': team_metrics.average_cost_per_employee
            },
            'cost_analysis': {
                'total_cost': cost_analysis.total_cost,
                'regular_cost': cost_analysis.regular_cost,
                'overtime_cost': cost_analysis.overtime_cost,
                'overtime_percentage': cost_analysis.overtime_cost_percentage,
                'cost_per_project': cost_analysis.cost_per_project,
                'cost_per_hour': cost_analysis.cost_per_hour
            },
            'workforce_sizing': {
                'current_headcount': workforce_recommendation.current_headcount,
                'recommended_headcount': workforce_recommendation.recommended_headcount,
                'reasoning': workforce_recommendation.reasoning,
                'expected_cost_impact': workforce_recommendation.expected_cost_impact,
                'expected_overtime_reduction': workforce_recommendation.expected_overtime_reduction,
                'confidence_level': workforce_recommendation.confidence_level
            },
            'top_utilized_employees': [
                {
                    'name': m.employee_name,
                    'utilization_rate': m.utilization_rate,
                    'total_hours': m.total_hours,
                    'overtime_percentage': m.overtime_percentage
                }
                for m in top_utilized
            ],
            'underutilized_employees': [
                {
                    'name': m.employee_name,
                    'utilization_rate': m.utilization_rate,
                    'total_hours': m.total_hours,
                    'num_assignments': m.num_assignments
                }
                for m in underutilized
            ],
            'overworked_employees': [
                {
                    'name': m.employee_name,
                    'overtime_hours': m.overtime_hours,
                    'overtime_percentage': m.overtime_percentage,
                    'total_cost': m.total_cost
                }
                for m in overworked
            ],
            'overtime_vs_hiring': overtime_comparison
        }
    
    def export_report_to_dict(self) -> Dict[str, Any]:
        return self.generate_capacity_report()


def analyze_capacity(schedule: Schedule, analysis_period_days: int = 365) -> Dict[str, Any]:
    analyzer = CapacityAnalyzer(schedule, analysis_period_days)
    return analyzer.generate_capacity_report()
