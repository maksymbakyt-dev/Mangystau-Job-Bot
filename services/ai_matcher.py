import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Resume, Vacancy

async def get_top_vacancies_for_resume(session: AsyncSession, resume_id: int):
    result = await session.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    
    if not resume:
        return []

    result = await session.execute(select(Vacancy))
    vacancies = result.scalars().all()
    
    if not vacancies:
        return []

    seeker_text = f"{resume.skills} {resume.experience} {resume.languages}"
    vacancy_texts = [f"{v.skills_required} {v.description} {v.languages_required}" for v in vacancies]
    
    vectorizer = TfidfVectorizer(stop_words=None) 
    try:
        all_texts = [seeker_text] + vacancy_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        matches = []
        for idx, similarity in enumerate(cosine_similarities):
            matches.append({
                'vacancy': vacancies[idx],
                'match_percent': round(similarity * 100, 1)
            })
            
        matches.sort(key=lambda x: x['match_percent'], reverse=True)
        matches = [m for m in matches if m['match_percent'] > 0]
        return matches[:3]
    except Exception as e:
        print(f"Ошибка матчинга: {e}")
        return []

async def get_top_resumes_for_vacancy(session: AsyncSession, vacancy_id: int):
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    vacancy = result.scalar_one_or_none()
    
    if not vacancy:
        return []

    result = await session.execute(select(Resume))
    resumes = result.scalars().all()
    
    if not resumes:
        return []

    vacancy_text = f"{vacancy.skills_required} {vacancy.description} {vacancy.languages_required}"
    resume_texts = [f"{r.skills} {r.experience} {r.languages}" for r in resumes]
    
    vectorizer = TfidfVectorizer()
    try:
        all_texts = [vacancy_text] + resume_texts
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        
        matches = []
        for idx, similarity in enumerate(cosine_similarities):
            matches.append({
                'resume': resumes[idx],
                'match_percent': round(similarity * 100, 1)
            })
            
        matches.sort(key=lambda x: x['match_percent'], reverse=True)
        matches = [m for m in matches if m['match_percent'] > 0]
        return matches[:3]
    except Exception as e:
        print(f"Ошибка матчинга: {e}")
        return []
