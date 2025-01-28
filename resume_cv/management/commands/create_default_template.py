from django.core.management.base import BaseCommand
from resume_cv.models import ResumeCvCategory, ResumeCvTemplate

DEFAULT_TEMPLATE_HTML = """
<div id="resumecv-layout" class="resumecv-layout">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <div class="header text-center">
                    <h1>Your Name</h1>
                    <p>Professional Title</p>
                </div>
                <div class="contact-info text-center">
                    <p>Email: your.email@example.com | Phone: (123) 456-7890</p>
                    <p>Location: City, Country</p>
                </div>
                <div class="section">
                    <h2>Professional Summary</h2>
                    <p>A brief overview of your professional background and key strengths.</p>
                </div>
                <div class="section">
                    <h2>Work Experience</h2>
                    <div class="experience-item">
                        <h3>Job Title</h3>
                        <p>Company Name | Date - Present</p>
                        <ul>
                            <li>Key achievement or responsibility</li>
                            <li>Another key achievement</li>
                        </ul>
                    </div>
                </div>
                <div class="section">
                    <h2>Education</h2>
                    <div class="education-item">
                        <h3>Degree Name</h3>
                        <p>Institution Name | Graduation Year</p>
                    </div>
                </div>
                <div class="section">
                    <h2>Skills</h2>
                    <ul class="skills-list">
                        <li>Skill 1</li>
                        <li>Skill 2</li>
                        <li>Skill 3</li>
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
"""

DEFAULT_TEMPLATE_CSS = """
#resumecv-layout {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
    padding: 30px;
}

.header {
    margin-bottom: 30px;
}

.header h1 {
    color: #2c3e50;
    margin-bottom: 5px;
}

.contact-info {
    margin-bottom: 30px;
}

.section {
    margin-bottom: 25px;
}

.section h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 5px;
    margin-bottom: 15px;
}

.experience-item, .education-item {
    margin-bottom: 20px;
}

.experience-item h3, .education-item h3 {
    color: #34495e;
    margin-bottom: 5px;
}

.skills-list {
    list-style: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.skills-list li {
    background: #f0f0f0;
    padding: 5px 15px;
    border-radius: 15px;
    font-size: 14px;
}
"""

class Command(BaseCommand):
    help = 'Creates a default resume template'

    def handle(self, *args, **kwargs):
        # Create default category if it doesn't exist
        category, created = ResumeCvCategory.objects.get_or_create(
            name="Professional",
            defaults={
                'color': '#007bff'
            }
        )
        
        # Create default template if it doesn't exist
        template, created = ResumeCvTemplate.objects.get_or_create(
            name="Default Professional Template",
            defaults={
                'category': category,
                'content': DEFAULT_TEMPLATE_HTML,
                'style': DEFAULT_TEMPLATE_CSS,
                'active': True,
                'is_premium': False
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created default template'))
        else:
            self.stdout.write(self.style.SUCCESS('Default template already exists')) 