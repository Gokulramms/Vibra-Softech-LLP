"""
Data Generator for Resource Scheduling System

Generates realistic test data for:
- 100 employees with varied skill distributions
- 100 projects with realistic time windows
- Configurable scenarios for testing
"""

import random
from datetime import datetime, timedelta
from typing import List, Set, Tuple, Dict, Any
import json

from .models import (
    Employee, Project, Schedule, TimeSlot, SkillType, ProjectStatus
)


class DataGenerator:
    """Generate realistic test data for scheduling system"""
    
    def __init__(self, seed: int = 42):
        """
        Initialize data generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        random.seed(seed)
        self.seed = seed
    
    def generate_employee_name(self, employee_id: int) -> str:
        """Generate a realistic employee name"""
        first_names = [
            "Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn",
            "Sam", "Jamie", "Drew", "Blake", "Cameron", "Dakota", "Emerson", "Finley",
            "Harper", "Hayden", "Jesse", "Kendall", "Logan", "Parker", "Peyton", "Reese",
            "Rowan", "Sage", "Skyler", "Spencer", "Sydney", "Tyler", "Adrian", "Angel",
            "Ashton", "Bailey", "Charlie", "Chris", "Devon", "Dylan", "Eden", "Ellis",
            "Frankie", "Gray", "Hunter", "Indigo", "Justice", "Kai", "Lane", "Lee",
            "London", "Marley", "Max", "Micah", "Noah", "Ocean", "Phoenix", "River",
            "Robin", "Rory", "Ryan", "Sawyer", "Shawn", "Sloan", "Storm", "Tatum",
            "Teagan", "Val", "Winter", "Zion", "Arden", "Aspen", "Aubrey", "August",
            "Bellamy", "Blair", "Briar", "Brooklyn", "Carson", "Carter", "Cedar", "Chandler",
            "Charlie", "Cody", "Corey", "Dallas", "Darcy", "Devin", "Elliot", "Ellis",
            "Emery", "Evan", "Ezra", "Fallon", "Flynn", "Gale", "Glenn", "Greer",
            "Harley", "Haven", "Holland", "Hollis", "Indiana", "Ivory", "Jaden", "Jules"
        ]
        
        last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
            "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
            "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
            "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
            "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
            "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
            "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
            "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers"
        ]
        
        first = random.choice(first_names)
        last = random.choice(last_names)
        return f"{first} {last}"
    
    def generate_employee_skills(self) -> Set[SkillType]:
        """
        Generate a realistic set of skills for an employee.
        Most employees have 1-3 skills, some specialists have more.
        """
        all_skills = list(SkillType)
        
        # 60% have 1 skill (specialists)
        # 30% have 2 skills
        # 10% have 3+ skills (versatile)
        
        rand = random.random()
        if rand < 0.6:
            num_skills = 1
        elif rand < 0.9:
            num_skills = 2
        else:
            num_skills = random.randint(3, 4)
        
        return set(random.sample(all_skills, num_skills))
    
    def generate_employees(self, count: int = 100) -> List[Employee]:
        employees = []
        
        all_skills = list(SkillType)
        num_skills = len(all_skills)
        
        employees_per_skill = count // num_skills
        
        for i in range(count):
            employee_id = i + 1
            name = self.generate_employee_name(employee_id)
            
            if i < num_skills * employees_per_skill:
                primary_skill_index = i % num_skills
                primary_skill = all_skills[primary_skill_index]
                skills = {primary_skill}
                
                if random.random() < 0.4:
                    other_skills = [s for s in all_skills if s != primary_skill]
                    skills.add(random.choice(other_skills))
            else:
                skills = self.generate_employee_skills()
            
            employee = Employee(
                id=employee_id,
                name=name,
                skills=skills
            )
            employees.append(employee)
        
        return employees
    
    def generate_project_name(self, project_id: int) -> str:
        """Generate a realistic project name"""
        project_types = [
            "Live Sports", "News Broadcast", "Entertainment Show", "Concert",
            "Award Ceremony", "Talk Show", "Game Show", "Reality Show",
            "Documentary", "Special Event", "Press Conference", "Panel Discussion",
            "Webinar", "Product Launch", "Corporate Event", "Festival Coverage"
        ]
        
        adjectives = [
            "Premier", "Elite", "Grand", "Special", "Annual", "Weekly",
            "Daily", "Prime", "Exclusive", "Live", "Breaking", "Featured"
        ]
        
        project_type = random.choice(project_types)
        adjective = random.choice(adjectives)
        
        return f"{adjective} {project_type} #{project_id}"
    
    def generate_project_time_slot(
        self,
        start_date: datetime,
        end_date: datetime,
        min_duration_hours: float = 2.0,
        max_duration_hours: float = 8.0
    ) -> TimeSlot:
        """
        Generate a random time slot for a project.
        
        Args:
            start_date: Earliest possible start date
            end_date: Latest possible start date
            min_duration_hours: Minimum project duration
            max_duration_hours: Maximum project duration
        
        Returns:
            TimeSlot object
        """
        # Random day within range
        days_range = (end_date - start_date).days
        random_day = start_date + timedelta(days=random.randint(0, days_range))
        
        # Random start hour (6 AM to 8 PM)
        start_hour = random.randint(6, 20)
        project_start = random_day.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        # Random duration
        duration = random.uniform(min_duration_hours, max_duration_hours)
        project_end = project_start + timedelta(hours=duration)
        
        return TimeSlot(start=project_start, end=project_end)
    
    def generate_projects(
        self,
        count: int = 100,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Project]:
        """
        Generate a list of projects with realistic requirements.
        
        Args:
            count: Number of projects to generate
            start_date: Start of project period
            end_date: End of project period
        
        Returns:
            List of Project objects
        """
        if start_date is None:
            start_date = datetime(2026, 1, 1)
        
        if end_date is None:
            end_date = datetime(2026, 12, 31)
        
        projects = []
        all_skills = list(SkillType)
        
        for i in range(count):
            project_id = i + 1
            name = self.generate_project_name(project_id)
            time_slot = self.generate_project_time_slot(start_date, end_date)
            
            # Each project requires exactly 5 different skills
            required_skills = random.sample(all_skills, 5)
            
            # Random priority (1-10)
            priority = random.randint(1, 10)
            
            # Most projects are fixed (90%)
            is_fixed = random.random() < 0.9
            
            project = Project(
                id=project_id,
                name=name,
                time_slot=time_slot,
                required_skills=required_skills,
                priority=priority,
                is_fixed=is_fixed
            )
            projects.append(project)
        
        return projects
    
    def generate_schedule(
        self,
        num_employees: int = 100,
        num_projects: int = 100,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Schedule:
        """
        Generate a complete schedule with employees and projects.
        
        Args:
            num_employees: Number of employees
            num_projects: Number of projects
            start_date: Start of project period
            end_date: End of project period
        
        Returns:
            Schedule object
        """
        schedule = Schedule()
        
        # Generate employees
        employees = self.generate_employees(num_employees)
        for emp in employees:
            schedule.add_employee(emp)
        
        # Generate projects
        projects = self.generate_projects(num_projects, start_date, end_date)
        for proj in projects:
            schedule.add_project(proj)
        
        return schedule
    
    def generate_scenario(
        self,
        scenario_name: str,
        **kwargs
    ) -> Tuple[Schedule, Dict[str, Any]]:
        """
        Generate a specific test scenario.
        
        Args:
            scenario_name: Name of the scenario
            **kwargs: Additional parameters
        
        Returns:
            Tuple of (Schedule, scenario_metadata)
        """
        scenarios = {
            'balanced': {
                'num_employees': 100,
                'num_projects': 100,
                'description': 'Balanced scenario with equal employees and projects'
            },
            'understaffed': {
                'num_employees': 80,
                'num_projects': 100,
                'description': 'Understaffed scenario with more projects than optimal'
            },
            'overstaffed': {
                'num_employees': 120,
                'num_projects': 100,
                'description': 'Overstaffed scenario with excess capacity'
            },
            'peak_season': {
                'num_employees': 100,
                'num_projects': 150,
                'description': 'Peak season with high project volume'
            },
            'low_season': {
                'num_employees': 100,
                'num_projects': 60,
                'description': 'Low season with reduced project volume'
            }
        }
        
        if scenario_name not in scenarios:
            raise ValueError(f"Unknown scenario: {scenario_name}")
        
        scenario_config = scenarios[scenario_name]
        scenario_config.update(kwargs)
        
        schedule = self.generate_schedule(
            num_employees=scenario_config['num_employees'],
            num_projects=scenario_config['num_projects'],
            start_date=scenario_config.get('start_date'),
            end_date=scenario_config.get('end_date')
        )
        
        metadata = {
            'scenario_name': scenario_name,
            'description': scenario_config['description'],
            'num_employees': scenario_config['num_employees'],
            'num_projects': scenario_config['num_projects'],
            'seed': self.seed
        }
        
        return schedule, metadata
    
    def save_schedule_to_file(self, schedule: Schedule, filename: str) -> None:
        """
        Save generated schedule to JSON file.
        
        Args:
            schedule: Schedule to save
            filename: Output filename
        """
        data = schedule.to_dict()
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Schedule saved to {filename}")


def generate_test_data(
    num_employees: int = 100,
    num_projects: int = 100,
    seed: int = 42
) -> Schedule:
    """
    Convenience function to generate test data.
    
    Args:
        num_employees: Number of employees
        num_projects: Number of projects
        seed: Random seed
    
    Returns:
        Schedule object
    """
    generator = DataGenerator(seed=seed)
    return generator.generate_schedule(num_employees, num_projects)


# Example usage
if __name__ == "__main__":
    print("Generating test data...")
    
    generator = DataGenerator(seed=42)
    
    # Generate balanced scenario
    schedule, metadata = generator.generate_scenario('balanced')
    
    print(f"\nScenario: {metadata['scenario_name']}")
    print(f"Description: {metadata['description']}")
    print(f"Employees: {metadata['num_employees']}")
    print(f"Projects: {metadata['num_projects']}")
    
    print(f"\nGenerated {len(schedule.employees)} employees")
    print(f"Generated {len(schedule.projects)} projects")
    
    # Show skill distribution
    skill_counts = {skill: 0 for skill in SkillType}
    for emp in schedule.employees:
        for skill in emp.skills:
            skill_counts[skill] += 1
    
    print("\nSkill Distribution:")
    for skill, count in skill_counts.items():
        print(f"  {skill.value}: {count} employees")
    
    # Save to file
    generator.save_schedule_to_file(schedule, "test_schedule.json")
    
    print("\nTest data generation complete!")
