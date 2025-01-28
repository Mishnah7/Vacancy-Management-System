from django.core.management.base import BaseCommand
from resume_cv.models import ResumeCvCategory, ResumeCvTemplate

# Modern Split Layout Template
MODERN_SPLIT_HTML = """
<div id="resumecv-layout" class="split-layout">
    <div class="sidebar">
        <div class="profile-section">
            <div class="profile-image"></div>
            <h1>Your Name</h1>
            <p class="title">Professional Title</p>
        </div>
        
        <div class="contact-section">
            <h3>Contact</h3>
            <ul>
                <li><i class="fas fa-envelope"></i> email@example.com</li>
                <li><i class="fas fa-phone"></i> (123) 456-7890</li>
                <li><i class="fas fa-map-marker-alt"></i> City, Country</li>
                <li><i class="fab fa-linkedin"></i> linkedin.com/in/yourprofile</li>
            </ul>
        </div>
        
        <div class="skills-section">
            <h3>Skills</h3>
            <div class="skill-bars">
                <div class="skill">
                    <span>Skill 1</span>
                    <div class="skill-bar" data-level="90"></div>
                </div>
                <div class="skill">
                    <span>Skill 2</span>
                    <div class="skill-bar" data-level="85"></div>
                </div>
                <div class="skill">
                    <span>Skill 3</span>
                    <div class="skill-bar" data-level="75"></div>
                </div>
            </div>
        </div>
    </div>

    <div class="main-content">
        <div class="section summary">
            <h2>Professional Summary</h2>
            <p>Your professional summary goes here...</p>
        </div>

        <div class="section experience">
            <h2>Work Experience</h2>
            <div class="timeline">
                <div class="timeline-item">
                    <div class="date">2020 - Present</div>
                    <div class="content">
                        <h3>Job Title</h3>
                        <h4>Company Name</h4>
                        <ul>
                            <li>Achievement 1</li>
                            <li>Achievement 2</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <div class="section education">
            <h2>Education</h2>
            <div class="education-item">
                <h3>Degree Name</h3>
                <p>University Name | 2015-2019</p>
                <p>Relevant coursework and achievements</p>
            </div>
        </div>
    </div>
</div>
"""

MODERN_SPLIT_CSS = """
.split-layout {
    display: grid;
    grid-template-columns: 300px 1fr;
    min-height: 100vh;
    font-family: 'Roboto', sans-serif;
}

.sidebar {
    background: #2c3e50;
    color: white;
    padding: 30px;
}

.profile-section {
    text-align: center;
    margin-bottom: 30px;
}

.profile-image {
    width: 150px;
    height: 150px;
    border-radius: 50%;
    margin: 0 auto 20px;
    background: #34495e;
}

.contact-section ul {
    list-style: none;
    padding: 0;
}

.contact-section li {
    margin-bottom: 10px;
}

.contact-section i {
    width: 20px;
    margin-right: 10px;
}

.skill-bars .skill {
    margin-bottom: 15px;
}

.skill-bar {
    height: 6px;
    background: #34495e;
    border-radius: 3px;
    position: relative;
}

.skill-bar::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background: #3498db;
    border-radius: 3px;
    width: attr(data-level);
}

.main-content {
    padding: 40px;
    background: #fff;
}

.section {
    margin-bottom: 30px;
}

.section h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
}

.timeline {
    position: relative;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 2px;
    background: #3498db;
}

.timeline-item {
    padding-left: 30px;
    position: relative;
    margin-bottom: 30px;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -4px;
    top: 0;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #3498db;
}

.date {
    color: #7f8c8d;
    margin-bottom: 5px;
}
"""

# Creative Minimal Template
MINIMAL_HTML = """
<div id="resumecv-layout" class="minimal-layout">
    <header>
        <h1 class="name">Your Name</h1>
        <p class="title">Professional Title</p>
        <div class="contact-bar">
            <span><i class="fas fa-envelope"></i> email@example.com</span>
            <span><i class="fas fa-phone"></i> (123) 456-7890</span>
            <span><i class="fas fa-map-marker-alt"></i> City, Country</span>
        </div>
    </header>

    <section class="summary">
        <p class="lead">A brief, impactful statement about your professional journey and aspirations.</p>
    </section>

    <section class="experience">
        <h2>Experience</h2>
        <div class="experience-grid">
            <div class="experience-item">
                <div class="year">2020</div>
                <div class="details">
                    <h3>Job Title</h3>
                    <h4>Company Name</h4>
                    <ul>
                        <li>Key achievement with measurable results</li>
                        <li>Notable project or responsibility</li>
                    </ul>
                </div>
            </div>
        </div>
    </section>

    <section class="skills-education">
        <div class="skills">
            <h2>Skills</h2>
            <div class="tags">
                <span class="tag">Skill 1</span>
                <span class="tag">Skill 2</span>
                <span class="tag">Skill 3</span>
            </div>
        </div>
        
        <div class="education">
            <h2>Education</h2>
            <div class="education-item">
                <h3>Degree Name</h3>
                <p>University Name, Year</p>
            </div>
        </div>
    </section>
</div>
"""

MINIMAL_CSS = """
.minimal-layout {
    font-family: 'Inter', sans-serif;
    max-width: 900px;
    margin: 0 auto;
    padding: 40px;
    color: #2d3436;
    line-height: 1.6;
}

header {
    text-align: center;
    margin-bottom: 60px;
}

.name {
    font-size: 3em;
    font-weight: 700;
    margin: 0;
    letter-spacing: -1px;
}

.title {
    font-size: 1.2em;
    color: #636e72;
    margin: 10px 0 20px;
}

.contact-bar {
    display: flex;
    justify-content: center;
    gap: 30px;
    color: #636e72;
}

.contact-bar i {
    color: #0984e3;
    margin-right: 5px;
}

.lead {
    font-size: 1.2em;
    color: #2d3436;
    text-align: center;
    max-width: 700px;
    margin: 0 auto 60px;
    line-height: 1.8;
}

section {
    margin-bottom: 50px;
}

h2 {
    font-size: 1.5em;
    font-weight: 600;
    margin-bottom: 30px;
    position: relative;
    display: inline-block;
}

h2::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 100%;
    height: 2px;
    background: #0984e3;
}

.experience-grid {
    display: grid;
    gap: 30px;
}

.experience-item {
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 20px;
}

.year {
    font-weight: 600;
    color: #0984e3;
}

.details h3 {
    font-size: 1.2em;
    margin: 0;
}

.details h4 {
    color: #636e72;
    font-size: 1em;
    margin: 5px 0 10px;
}

.details ul {
    margin: 0;
    padding-left: 20px;
}

.skills-education {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.tag {
    background: #e1f5fe;
    color: #0984e3;
    padding: 5px 15px;
    border-radius: 20px;
    font-size: 0.9em;
}

.education-item {
    margin-bottom: 20px;
}

.education-item h3 {
    margin: 0;
    font-size: 1.1em;
}

.education-item p {
    color: #636e72;
    margin: 5px 0 0;
}

@media (max-width: 768px) {
    .contact-bar {
        flex-direction: column;
        gap: 10px;
    }
    
    .experience-item {
        grid-template-columns: 1fr;
    }
    
    .skills-education {
        grid-template-columns: 1fr;
    }
}
"""

# Corporate Professional Template
CORPORATE_HTML = """
<div id="resumecv-layout" class="corporate-layout">
    <div class="header">
        <div class="name-title">
            <h1>Your Name</h1>
            <div class="title-bar"></div>
            <p class="professional-title">Professional Title</p>
        </div>
        <div class="contact-info">
            <div class="contact-item">
                <i class="fas fa-envelope"></i>
                <span>email@example.com</span>
            </div>
            <div class="contact-item">
                <i class="fas fa-phone"></i>
                <span>(123) 456-7890</span>
            </div>
            <div class="contact-item">
                <i class="fas fa-map-marker-alt"></i>
                <span>City, Country</span>
            </div>
        </div>
    </div>

    <div class="main-content">
        <section class="professional-summary">
            <h2>Professional Summary</h2>
            <p>A concise overview of your career achievements and professional expertise.</p>
        </section>

        <section class="experience">
            <h2>Professional Experience</h2>
            <div class="experience-item">
                <div class="company-header">
                    <div class="company-info">
                        <h3>Job Title</h3>
                        <h4>Company Name</h4>
                    </div>
                    <div class="date-location">
                        <span>2020 - Present</span>
                        <span>City, Country</span>
                    </div>
                </div>
                <ul class="achievements">
                    <li>Key achievement with quantifiable results</li>
                    <li>Leadership or project management highlight</li>
                </ul>
            </div>
        </section>

        <div class="two-column">
            <section class="education">
                <h2>Education</h2>
                <div class="education-item">
                    <h3>Degree Name</h3>
                    <p>University Name</p>
                    <span class="year">Graduation Year</span>
                </div>
            </section>

            <section class="skills">
                <h2>Core Competencies</h2>
                <div class="skills-grid">
                    <div class="skill-item">
                        <span class="skill-name">Skill 1</span>
                        <div class="skill-level expert"></div>
                    </div>
                    <div class="skill-item">
                        <span class="skill-name">Skill 2</span>
                        <div class="skill-level advanced"></div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</div>
"""

CORPORATE_CSS = """
.corporate-layout {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    max-width: 1000px;
    margin: 0 auto;
    padding: 40px;
    color: #333;
    background: #fff;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 50px;
}

.name-title h1 {
    font-size: 2.5em;
    margin: 0;
    color: #1a237e;
}

.title-bar {
    width: 60px;
    height: 4px;
    background: #1a237e;
    margin: 15px 0;
}

.professional-title {
    font-size: 1.2em;
    color: #666;
    margin: 0;
}

.contact-info {
    text-align: right;
}

.contact-item {
    margin-bottom: 10px;
}

.contact-item i {
    color: #1a237e;
    margin-right: 10px;
    width: 20px;
    text-align: center;
}

.main-content section {
    margin-bottom: 40px;
}

h2 {
    color: #1a237e;
    font-size: 1.5em;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e8eaf6;
}

.experience-item {
    margin-bottom: 30px;
}

.company-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
}

.company-info h3 {
    font-size: 1.2em;
    margin: 0;
    color: #283593;
}

.company-info h4 {
    font-size: 1.1em;
    margin: 5px 0;
    color: #666;
}

.date-location {
    text-align: right;
    color: #666;
}

.date-location span {
    display: block;
    margin-bottom: 5px;
}

.achievements {
    margin: 0;
    padding-left: 20px;
}

.achievements li {
    margin-bottom: 8px;
}

.two-column {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
}

.education-item {
    margin-bottom: 20px;
}

.education-item h3 {
    margin: 0;
    color: #283593;
}

.education-item p {
    margin: 5px 0;
    color: #666;
}

.year {
    color: #666;
    font-size: 0.9em;
}

.skills-grid {
    display: grid;
    gap: 15px;
}

.skill-item {
    display: grid;
    grid-template-columns: 1fr 150px;
    align-items: center;
    gap: 15px;
}

.skill-level {
    height: 8px;
    background: #e8eaf6;
    border-radius: 4px;
    position: relative;
}

.skill-level::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background: #1a237e;
    border-radius: 4px;
}

.expert::before {
    width: 90%;
}

.advanced::before {
    width: 75%;
}

@media (max-width: 768px) {
    .header {
        flex-direction: column;
        text-align: center;
    }
    
    .contact-info {
        text-align: center;
        margin-top: 20px;
    }
    
    .two-column {
        grid-template-columns: 1fr;
    }
    
    .company-header {
        flex-direction: column;
        text-align: center;
    }
    
    .date-location {
        text-align: center;
        margin-top: 10px;
    }
}
"""

class Command(BaseCommand):
    help = 'Creates diverse resume templates'

    def handle(self, *args, **kwargs):
        # Create categories
        modern_category, _ = ResumeCvCategory.objects.get_or_create(
            name="Modern",
            defaults={'color': '#3498db'}
        )
        
        minimal_category, _ = ResumeCvCategory.objects.get_or_create(
            name="Minimal",
            defaults={'color': '#0984e3'}
        )
        
        corporate_category, _ = ResumeCvCategory.objects.get_or_create(
            name="Corporate",
            defaults={'color': '#1a237e'}
        )
        
        # Create Modern Split template
        ResumeCvTemplate.objects.get_or_create(
            name="Modern Split",
            defaults={
                'category': modern_category,
                'content': MODERN_SPLIT_HTML,
                'style': MODERN_SPLIT_CSS,
                'active': True,
                'is_premium': True
            }
        )
        
        # Create Minimal template
        ResumeCvTemplate.objects.get_or_create(
            name="Creative Minimal",
            defaults={
                'category': minimal_category,
                'content': MINIMAL_HTML,
                'style': MINIMAL_CSS,
                'active': True,
                'is_premium': False
            }
        )
        
        # Create Corporate template
        ResumeCvTemplate.objects.get_or_create(
            name="Corporate Professional",
            defaults={
                'category': corporate_category,
                'content': CORPORATE_HTML,
                'style': CORPORATE_CSS,
                'active': True,
                'is_premium': True
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully created diverse resume templates')) 