from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Set, Dict, Optional, Any
from enum import Enum
import json


class SkillType(Enum):
    PRODUCER = "Producer"
    EDITOR = "Editor"
    GRAPHICS_DESIGNER = "Graphics Designer"
    COLORIST = "Colorist"
    AUDIO_ENGINEER = "Audio Engineer"


class ProjectStatus(Enum):
    PENDING = "Pending"
    SCHEDULED = "Scheduled"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


@dataclass
class TimeSlot:
    start: datetime
    end: datetime
    
    def __post_init__(self):
        if self.end <= self.start:
            raise ValueError(f"End time {self.end} must be after start time {self.start}")
    
    @property
    def duration_hours(self) -> float:
        return (self.end - self.start).total_seconds() / 3600
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        return not (self.end <= other.start or self.start >= other.end)
    
    def contains(self, dt: datetime) -> bool:
        return self.start <= dt < self.end
    
    def __repr__(self) -> str:
        return f"TimeSlot({self.start.strftime('%Y-%m-%d %H:%M')} - {self.end.strftime('%Y-%m-%d %H:%M')})"
    
    def to_dict(self) -> dict:
        return {
            'start': self.start.isoformat(),
            'end': self.end.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TimeSlot':
        return cls(
            start=datetime.fromisoformat(data['start']),
            end=datetime.fromisoformat(data['end'])
        )


@dataclass
class Employee:
    id: int
    name: str
    skills: Set[SkillType]
    regular_hours_worked: float = 0.0
    overtime_hours_worked: float = 0.0
    assignments: List['Assignment'] = field(default_factory=list)
    unavailable_slots: List[TimeSlot] = field(default_factory=list)
    
    MAX_REGULAR_HOURS_PER_DAY: float = 8.0
    REGULAR_RATE: float = 1.0
    OVERTIME_RATE: float = 1.3
    
    def has_skill(self, skill: SkillType) -> bool:
        return skill in self.skills
    
    def is_available(self, time_slot: TimeSlot) -> bool:
        for unavailable in self.unavailable_slots:
            if time_slot.overlaps_with(unavailable):
                return False
        
        for assignment in self.assignments:
            if time_slot.overlaps_with(assignment.time_slot):
                return False
        
        return True
    
    def add_assignment(self, assignment: 'Assignment') -> None:
        if not self.is_available(assignment.time_slot):
            raise ValueError(f"Employee {self.name} is not available for {assignment.time_slot}")
        
        self.assignments.append(assignment)
        self._update_hours(assignment.time_slot)
    
    def _update_hours(self, time_slot: TimeSlot) -> None:
        hours = time_slot.duration_hours
        assignment_date = time_slot.start.date()
        
        daily_hours = sum(
            a.time_slot.duration_hours 
            for a in self.assignments 
            if a.time_slot.start.date() == assignment_date
        )
        
        if daily_hours <= self.MAX_REGULAR_HOURS_PER_DAY:
            regular = min(hours, self.MAX_REGULAR_HOURS_PER_DAY - daily_hours)
            overtime = max(0, hours - regular)
        else:
            regular = 0
            overtime = hours
        
        self.regular_hours_worked += regular
        self.overtime_hours_worked += overtime
    
    def get_total_cost(self) -> float:
        regular_cost = self.regular_hours_worked * self.REGULAR_RATE
        overtime_cost = self.overtime_hours_worked * self.OVERTIME_RATE
        return regular_cost + overtime_cost
    
    def get_utilization_rate(self, total_available_hours: float) -> float:
        if total_available_hours <= 0:
            return 0.0
        
        total_hours = self.regular_hours_worked + self.overtime_hours_worked
        return (total_hours / total_available_hours) * 100
    
    def get_overtime_percentage(self) -> float:
        total_hours = self.regular_hours_worked + self.overtime_hours_worked
        if total_hours <= 0:
            return 0.0
        return (self.overtime_hours_worked / total_hours) * 100
    
    def reset_hours(self) -> None:
        self.regular_hours_worked = 0.0
        self.overtime_hours_worked = 0.0
        self.assignments.clear()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'skills': [skill.value for skill in self.skills],
            'regular_hours_worked': self.regular_hours_worked,
            'overtime_hours_worked': self.overtime_hours_worked,
            'assignments': [a.to_dict() for a in self.assignments],
            'unavailable_slots': [slot.to_dict() for slot in self.unavailable_slots]
        }
    
    def __repr__(self) -> str:
        return f"Employee(id={self.id}, name='{self.name}', skills={len(self.skills)})"


@dataclass
class Project:
    id: int
    name: str
    time_slot: TimeSlot
    required_skills: List[SkillType]
    assigned_employees: List[Employee] = field(default_factory=list)
    status: ProjectStatus = ProjectStatus.PENDING
    priority: int = 5
    is_fixed: bool = True
    
    def __post_init__(self):
        if len(self.required_skills) != 5:
            raise ValueError(f"Project must require exactly 5 skills, got {len(self.required_skills)}")
        
        if len(set(self.required_skills)) != 5:
            raise ValueError("All 5 required skills must be different")
    
    def is_fully_staffed(self) -> bool:
        return len(self.assigned_employees) == 5
    
    def get_missing_skills(self) -> List[SkillType]:
        missing = []
        
        for required_skill in self.required_skills:
            skill_covered = False
            for emp in self.assigned_employees:
                if emp.has_skill(required_skill):
                    skill_covered = True
                    break
            if not skill_covered:
                missing.append(required_skill)
        
        return missing
    
    def can_assign_employee(self, employee: Employee) -> bool:
        if employee in self.assigned_employees:
            return False
        
        if self.is_fully_staffed():
            return False
        
        missing_skills = self.get_missing_skills()
        if not any(employee.has_skill(skill) for skill in missing_skills):
            return False
        
        if not employee.is_available(self.time_slot):
            return False
        
        return True
    
    def assign_employee(self, employee: Employee) -> None:
        if not self.can_assign_employee(employee):
            raise ValueError(f"Cannot assign {employee.name} to project {self.name}")
        
        self.assigned_employees.append(employee)
        
        assignment = Assignment(
            employee=employee,
            project=self,
            time_slot=self.time_slot
        )
        employee.add_assignment(assignment)
        
        if self.is_fully_staffed():
            self.status = ProjectStatus.SCHEDULED
    
    def get_total_cost(self) -> float:
        return sum(
            emp.get_total_cost() 
            for emp in self.assigned_employees
        )
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'time_slot': self.time_slot.to_dict(),
            'required_skills': [skill.value for skill in self.required_skills],
            'assigned_employees': [emp.id for emp in self.assigned_employees],
            'status': self.status.value,
            'priority': self.priority,
            'is_fixed': self.is_fixed
        }
    
    def __repr__(self) -> str:
        return f"Project(id={self.id}, name='{self.name}', staffed={len(self.assigned_employees)}/5)"


@dataclass
class Assignment:
    employee: Employee
    project: Project
    time_slot: TimeSlot
    
    def get_cost(self) -> float:
        hours = self.time_slot.duration_hours
        assignment_date = self.time_slot.start.date()
        daily_hours = sum(
            a.time_slot.duration_hours 
            for a in self.employee.assignments 
            if a.time_slot.start.date() == assignment_date and a != self
        )
        
        if daily_hours < Employee.MAX_REGULAR_HOURS_PER_DAY:
            regular = min(hours, Employee.MAX_REGULAR_HOURS_PER_DAY - daily_hours)
            overtime = max(0, hours - regular)
        else:
            regular = 0
            overtime = hours
        
        return (regular * Employee.REGULAR_RATE) + (overtime * Employee.OVERTIME_RATE)
    
    def to_dict(self) -> dict:
        return {
            'employee_id': self.employee.id,
            'project_id': self.project.id,
            'time_slot': self.time_slot.to_dict()
        }
    
    def __repr__(self) -> str:
        return f"Assignment({self.employee.name} -> {self.project.name})"


@dataclass
class Schedule:
    employees: List[Employee] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    
    def add_employee(self, employee: Employee) -> None:
        if any(e.id == employee.id for e in self.employees):
            raise ValueError(f"Employee with ID {employee.id} already exists")
        self.employees.append(employee)
    
    def add_project(self, project: Project) -> None:
        if any(p.id == project.id for p in self.projects):
            raise ValueError(f"Project with ID {project.id} already exists")
        self.projects.append(project)
    
    def get_employee_by_id(self, employee_id: int) -> Optional[Employee]:
        return next((e for e in self.employees if e.id == employee_id), None)
    
    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        return next((p for p in self.projects if p.id == project_id), None)
    
    def get_unscheduled_projects(self) -> List[Project]:
        return [p for p in self.projects if not p.is_fully_staffed()]
    
    def get_available_employees(self, time_slot: TimeSlot, skill: SkillType) -> List[Employee]:
        return [
            emp for emp in self.employees
            if emp.has_skill(skill) and emp.is_available(time_slot)
        ]
    
    def validate_schedule(self) -> Dict[str, Any]:
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        for employee in self.employees:
            assignments = sorted(employee.assignments, key=lambda a: a.time_slot.start)
            for i in range(len(assignments) - 1):
                if assignments[i].time_slot.overlaps_with(assignments[i + 1].time_slot):
                    results['valid'] = False
                    results['errors'].append(
                        f"Employee {employee.name} has overlapping assignments: "
                        f"{assignments[i].project.name} and {assignments[i + 1].project.name}"
                    )
        
        unstaffed = self.get_unscheduled_projects()
        if unstaffed:
            results['warnings'].append(f"{len(unstaffed)} projects are not fully staffed")
        
        results['stats'] = {
            'total_employees': len(self.employees),
            'total_projects': len(self.projects),
            'fully_staffed_projects': len([p for p in self.projects if p.is_fully_staffed()]),
            'total_assignments': sum(len(e.assignments) for e in self.employees)
        }
        
        return results
    
    def get_total_cost(self) -> float:
        return sum(emp.get_total_cost() for emp in self.employees)
    
    def to_dict(self) -> dict:
        return {
            'employees': [emp.to_dict() for emp in self.employees],
            'projects': [proj.to_dict() for proj in self.projects]
        }
    
    def save_to_file(self, filename: str) -> None:
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    def __repr__(self) -> str:
        return f"Schedule(employees={len(self.employees)}, projects={len(self.projects)})"
