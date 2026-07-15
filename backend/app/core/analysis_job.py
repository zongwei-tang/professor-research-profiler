class AnalysisJob:
    def __init__(self, job_id, status, user_id, author_id, author_name, analysis_text, interest, language, provider):
        self.job_id = job_id
        self.status = status
        self.user_id = user_id
        self.author_id = author_id
        self.author_name = author_name
        self.analysis_text = analysis_text
        self.interest = interest
        self.language = language
        self.provider = provider
        self.provider_change = False

job_list = {}