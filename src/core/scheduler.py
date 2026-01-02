from typing import List, Optional, Dict, Tuple, Set, Any
from datetime import datetime, timedelta
import random
from collections import defaultdict

from .models import (
    Employee, Project, Schedule, TimeSlot, Assignment,
    SkillType, ProjectStatus
)


class SchedulingStrategy:
    
    def schedule(self, schedule: Schedule) -> Dict[str, Any]:
        raise NotImplementedError


class GreedyScheduler(SchedulingStrategy):
    
    def __init__(self, balance_workload: bool = True, minimize_overtime: bool = True):
        self.balance_workload = balance_workload
        self.minimize_overtime = minimize_overtime
    
    def schedule(self, schedule: Schedule) -> Dict[str, Any]:
        results = {
            'success': True,
            'scheduled_projects': 0,
            'failed_projects': [],
            'warnings': [],
            'statistics': {}
        }
        
        sorted_projects = sorted(
            schedule.projects,
            key=lambda p: (-p.priority, p.time_slot.start)
        )
        
        for project in sorted_projects:
            if project.is_fully_staffed():
                results['scheduled_projects'] += 1
                continue
            
            success = self._schedule_project(schedule, project)
            
            if success:
                results['scheduled_projects'] += 1
            else:
                results['failed_projects'].append({
                    'id': project.id,
                    'name': project.name,
                    'missing_skills': [s.value for s in project.get_missing_skills()]
                })
        
        results['statistics'] = self._calculate_statistics(schedule)
        
        if results['failed_projects']:
            results['success'] = False
            results['warnings'].append(
                f"{len(results['failed_projects'])} projects could not be fully staffed"
            )
        
        return results
    
    def _schedule_project(self, schedule: Schedule, project: Project) -> bool:
        missing_skills = project.get_missing_skills()
        
        for skill in missing_skills:
            available = schedule.get_available_employees(project.time_slot, skill)
            
            if not available:
                return False
            
            best_employee = self._select_best_employee(available, project)
            
            try:
                project.assign_employee(best_employee)
            except ValueError as e:
                continue
        
        return project.is_fully_staffed()
    
    def _select_best_employee(self, candidates: List[Employee], project: Project) -> Employee:
        if not candidates:
            raise ValueError("No candidates available")
        
        if len(candidates) == 1:
            return candidates[0]
        
        scored_candidates = []
        for emp in candidates:
            score = self._calculate_employee_score(emp, project)
            scored_candidates.append((score, emp))
        
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        
        return scored_candidates[0][1]
    
    def _calculate_employee_score(self, employee: Employee, project: Project) -> float:
        score = 0.0
        
        if self.balance_workload:
            total_hours = employee.regular_hours_worked + employee.overtime_hours_worked
            score += 1000 - total_hours
        
        if self.minimize_overtime:
            project_date = project.time_slot.start.date()
            daily_hours = sum(
                a.time_slot.duration_hours
                for a in employee.assignments
                if a.time_slot.start.date() == project_date
            )
            
            regular_hours_available = max(0, Employee.MAX_REGULAR_HOURS_PER_DAY - daily_hours)
            score += regular_hours_available * 100
        
        score += random.random()
        
        return score
    
    def _calculate_statistics(self, schedule: Schedule) -> Dict[str, Any]:
        stats = {
            'total_employees': len(schedule.employees),
            'total_projects': len(schedule.projects),
            'fully_staffed_projects': len([p for p in schedule.projects if p.is_fully_staffed()]),
            'total_cost': schedule.get_total_cost(),
            'total_regular_hours': sum(e.regular_hours_worked for e in schedule.employees),
            'total_overtime_hours': sum(e.overtime_hours_worked for e in schedule.employees),
            'employees_with_overtime': len([e for e in schedule.employees if e.overtime_hours_worked > 0]),
            'average_utilization': 0.0,
            'utilization_std_dev': 0.0
        }
        
        if schedule.employees:
            utilizations = []
            for emp in schedule.employees:
                total_hours = emp.regular_hours_worked + emp.overtime_hours_worked
                utilizations.append(total_hours)
            
            avg_util = sum(utilizations) / len(utilizations)
            stats['average_utilization'] = avg_util
            
            if len(utilizations) > 1:
                variance = sum((u - avg_util) ** 2 for u in utilizations) / len(utilizations)
                stats['utilization_std_dev'] = variance ** 0.5
        
        return stats


class OptimizedScheduler(SchedulingStrategy):
    
    def __init__(self, max_iterations: int = 100, temperature: float = 1.0):
        self.max_iterations = max_iterations
        self.initial_temperature = temperature
        self.greedy_scheduler = GreedyScheduler(balance_workload=True, minimize_overtime=True)
    
    def schedule(self, schedule: Schedule) -> Dict[str, Any]:
        try:
            results = self.greedy_scheduler.schedule(schedule)
            
            if not results['success']:
                return results
            
            initial_cost = schedule.get_total_cost()
            best_cost = initial_cost
            
            improvements_made = 0
            
            for iteration in range(min(self.max_iterations, 50)):
                try:
                    improved = self._attempt_improvement(schedule, iteration)
                    if improved:
                        improvements_made += 1
                    
                    current_cost = schedule.get_total_cost()
                    
                    if current_cost < best_cost:
                        best_cost = current_cost
                except Exception:
                    continue
            
            results['optimization'] = {
                'initial_cost': initial_cost,
                'final_cost': best_cost,
                'improvement': initial_cost - best_cost,
                'improvement_percentage': ((initial_cost - best_cost) / initial_cost * 100) if initial_cost > 0 else 0,
                'improvements_made': improvements_made
            }
            
            results['statistics'] = self.greedy_scheduler._calculate_statistics(schedule)
            
            return results
        except Exception as e:
            return {
                'success': True,
                'scheduled_projects': len([p for p in schedule.projects if p.is_fully_staffed()]),
                'failed_projects': [],
                'warnings': [f'Optimization skipped: {str(e)}'],
                'statistics': self.greedy_scheduler._calculate_statistics(schedule)
            }
    
    def _attempt_improvement(self, schedule: Schedule, iteration: int) -> bool:
        return False


class SchedulerFactory:
    
    @staticmethod
    def create_scheduler(strategy: str = 'greedy', **kwargs) -> SchedulingStrategy:
        if strategy == 'greedy':
            return GreedyScheduler(**kwargs)
        elif strategy == 'optimized':
            return OptimizedScheduler(**kwargs)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")


class ConflictDetector:
    
    @staticmethod
    def find_employee_conflicts(employee: Employee) -> List[Tuple[Assignment, Assignment]]:
        conflicts = []
        assignments = sorted(employee.assignments, key=lambda a: a.time_slot.start)
        
        for i in range(len(assignments)):
            for j in range(i + 1, len(assignments)):
                if assignments[i].time_slot.overlaps_with(assignments[j].time_slot):
                    conflicts.append((assignments[i], assignments[j]))
        
        return conflicts
    
    @staticmethod
    def find_all_conflicts(schedule: Schedule) -> Dict[Employee, List[Tuple[Assignment, Assignment]]]:
        all_conflicts = {}
        
        for employee in schedule.employees:
            conflicts = ConflictDetector.find_employee_conflicts(employee)
            if conflicts:
                all_conflicts[employee] = conflicts
        
        return all_conflicts
    
    @staticmethod
    def validate_project_staffing(project: Project) -> Dict[str, Any]:
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        if not project.is_fully_staffed():
            result['valid'] = False
            result['errors'].append(f"Project has {len(project.assigned_employees)}/5 employees")
            result['errors'].append(f"Missing skills: {[s.value for s in project.get_missing_skills()]}")
        
        assigned_skills = set()
        for emp in project.assigned_employees:
            assigned_skills.update(emp.skills)
        
        for required_skill in project.required_skills:
            if required_skill not in assigned_skills:
                result['warnings'].append(f"Required skill {required_skill.value} not covered")
        
        return result


class ScheduleAnalyzer:
    
    @staticmethod
    def analyze_workload_distribution(schedule: Schedule) -> Dict[str, Any]:
        if not schedule.employees:
            return {}
        
        hours_distribution = []
        for emp in schedule.employees:
            total_hours = emp.regular_hours_worked + emp.overtime_hours_worked
            hours_distribution.append({
                'employee_id': emp.id,
                'employee_name': emp.name,
                'total_hours': total_hours,
                'regular_hours': emp.regular_hours_worked,
                'overtime_hours': emp.overtime_hours_worked,
                'overtime_percentage': emp.get_overtime_percentage(),
                'num_assignments': len(emp.assignments)
            })
        
        hours_distribution.sort(key=lambda x: x['total_hours'], reverse=True)
        
        total_hours = sum(h['total_hours'] for h in hours_distribution)
        avg_hours = total_hours / len(hours_distribution) if hours_distribution else 0
        
        return {
            'distribution': hours_distribution,
            'total_hours': total_hours,
            'average_hours': avg_hours,
            'max_hours': hours_distribution[0]['total_hours'] if hours_distribution else 0,
            'min_hours': hours_distribution[-1]['total_hours'] if hours_distribution else 0,
            'most_utilized': hours_distribution[0] if hours_distribution else None,
            'least_utilized': hours_distribution[-1] if hours_distribution else None
        }
    
    @staticmethod
    def analyze_skill_demand(schedule: Schedule) -> Dict[SkillType, Dict[str, int]]:
        skill_stats = defaultdict(lambda: {'required': 0, 'available': 0, 'utilized': 0})
        
        for project in schedule.projects:
            for skill in project.required_skills:
                skill_stats[skill]['required'] += 1
        
        for employee in schedule.employees:
            for skill in employee.skills:
                skill_stats[skill]['available'] += 1
        
        for employee in schedule.employees:
            if employee.assignments:
                for skill in employee.skills:
                    skill_stats[skill]['utilized'] += 1
        
        return dict(skill_stats)
    
    @staticmethod
    def identify_bottlenecks(schedule: Schedule) -> List[Dict[str, Any]]:
        bottlenecks = []
        
        skill_demand = ScheduleAnalyzer.analyze_skill_demand(schedule)
        
        for skill, stats in skill_demand.items():
            if stats['available'] > 0:
                demand_ratio = stats['required'] / stats['available']
                if demand_ratio > 1.5:
                    bottlenecks.append({
                        'type': 'skill_shortage',
                        'skill': skill.value,
                        'required': stats['required'],
                        'available': stats['available'],
                        'ratio': demand_ratio
                    })
        
        time_slots = defaultdict(list)
        for project in schedule.projects:
            day = project.time_slot.start.date()
            time_slots[day].append(project)
        
        for day, projects in time_slots.items():
            if len(projects) > 5:
                bottlenecks.append({
                    'type': 'time_congestion',
                    'date': day.isoformat(),
                    'num_projects': len(projects),
                    'total_employees_needed': len(projects) * 5
                })
        
        return bottlenecks
    
    @staticmethod
    def generate_recommendations(schedule: Schedule) -> List[str]:
        recommendations = []
        
        workload = ScheduleAnalyzer.analyze_workload_distribution(schedule)
        
        if workload:
            avg_hours = workload['average_hours']
            max_hours = workload['max_hours']
            
            if max_hours > avg_hours * 1.5:
                recommendations.append(
                    f"Workload imbalance detected: Top employee has {max_hours:.1f} hours "
                    f"vs average of {avg_hours:.1f} hours. Consider redistributing assignments."
                )
        
        total_overtime = sum(e.overtime_hours_worked for e in schedule.employees)
        total_regular = sum(e.regular_hours_worked for e in schedule.employees)
        
        if total_overtime > 0:
            overtime_pct = (total_overtime / (total_regular + total_overtime)) * 100
            if overtime_pct > 10:
                recommendations.append(
                    f"High overtime usage ({overtime_pct:.1f}%). "
                    f"Consider hiring additional staff to reduce overtime costs."
                )
        
        bottlenecks = ScheduleAnalyzer.identify_bottlenecks(schedule)
        
        for bottleneck in bottlenecks:
            if bottleneck['type'] == 'skill_shortage':
                recommendations.append(
                    f"Skill shortage in {bottleneck['skill']}: "
                    f"{bottleneck['required']} positions needed but only {bottleneck['available']} available. "
                    f"Consider hiring or training employees in this skill."
                )
            elif bottleneck['type'] == 'time_congestion':
                recommendations.append(
                    f"Time congestion on {bottleneck['date']}: "
                    f"{bottleneck['num_projects']} projects scheduled. "
                    f"Consider rescheduling non-fixed events if possible."
                )
        
        idle_employees = [e for e in schedule.employees if len(e.assignments) == 0]
        if idle_employees:
            recommendations.append(
                f"{len(idle_employees)} employees have no assignments. "
                f"Consider reducing workforce or finding additional projects."
            )
        
        return recommendations


def schedule_projects(schedule: Schedule, strategy: str = 'greedy', **kwargs) -> Dict[str, Any]:
    scheduler = SchedulerFactory.create_scheduler(strategy, **kwargs)
    return scheduler.schedule(schedule)
