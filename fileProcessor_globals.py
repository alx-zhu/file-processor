BASE_FOLDER_NAME = 'to_process'
EMAIL_FOLDER_NAME = 'to_email'
EMAIL_BODY = """\
<p>Dear {name},</p>

<p>I hope this email finds you well. My name is Anika. I&rsquo;m an Executive Assistant that&rsquo;s part of the StudyFind team.</p>

<p>StudyFind is a startup attempting to build a registry that aims to diversify clinical trials and research studies! Our research has led us to believe that you are the best person to reach out to regarding our Surveys.</p>

<p>Our team has been working tirelessly to compose a survey that recognizes the trials and tribulations that impact various communities. The survey also contains a section where individuals can volunteer to participate in the StudyFind registry, which would only require their contact information.</p>

<p>Survey Below:<br>
<a href="http://bit.ly/3Xh3ejO">Survey Link</a></p>

<p>If you or anyone in your network would benefit from a diversified participant base or would benefit from being on a diverse research registry, we&rsquo;d appreciate your participation or willingness to share this with them.</p>

<p>Thank you for taking the time to read this! If you have any questions or concerns, please don&rsquo;t hesitate to contact me.</p>

<p>Sincerely, <br>
Anika Shah<br>
StudyFind | Executive Assistant | <a href="http://www.StudyFind.org">www.StudyFind.org</a><br>
San Jose State University | Business Administration: Management<br>
<a href="Anika.Shah03@StudyFind.org"> Anika.Shah03@StudyFind.org</a><br>
</p>
"""

SUBJECT_LINES = ["Diversifying Clinical Trials", "Help Diversify Clinical Trials", "Help Increase Accessibility to Clinical Trials"]
TERMS = ['Hispanic', 'White OR Caucasian', 'Black OR African American','American Indian OR Alaska Native', 'Asian American OR Pacific Islander']

# COUNTRY_TERMS = ['Africa'
# 'Central America'
# 'East Asia'
# 'Japan'
# 'Europe'
# 'Middle East'
# 'North America'
# 'Canada'
# 'Greenland'
# 'Mexico'
# 'United States'
# 'North Asia'
# 'Pacifica'
# 'South America'
# 'South Asia'
# 'Southeast Asia']

COUNTRY_TERMS = []

DISEASE_TERMS = [
'Essential hypertension',
'Diabetes mellitus',
'Osteoarthritis',
'Depressive disorders NOT bipolar depression NOT adjustment reaction with depressed mood',
'Acute respiratory infection',
'Retinal detachment',
'Retinal disorder',
'Diabetic retinopathy',
'Joint disorder',
'Cataracts NOT diabetic cataracts',
'Hyperlipidemias',
'Spine NOT low back pain',
'Attention-deficit hyperactivity disorder OR ADHD',
'Otitis media',
'Eustachian tube disorder',
'Acute pharyngitis',
'Obstructive sleep apnea OR sleep apnea NOS',
'Glaucoma',
'Coronary atherosclerosis',
'Gastroesophageal reflux disease',
'Acute and chronic sinusiti',
'Allergic rhinitis',
'Cardiac dysrhythmias NOT ventricular fibrillation'
]

# GROUPS_TERMS = [
# 'Hispanic'
# 'White'
# 'Black or African American'
# 'American Indian or Alaska Native'
# 'Asian American or Pacific Islander'
# ]