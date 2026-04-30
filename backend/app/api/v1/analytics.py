from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
import json
from datetime import datetime

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.survey import Survey
from app.models.question import Question
from app.models.response import Response as SurveyResponse, Answer
from app.models.user import User

router = APIRouter()

@router.post("/export/{survey_id}")
async def export_analytics(
    survey_id: int,
    export_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export survey analytics data in various formats"""
    # Get survey
    survey = db.query(Survey).filter(Survey.id == survey_id).first()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    
    # Get questions
    questions = db.query(Question).filter(Question.survey_id == survey_id).order_by(Question.order_index).all()
    
    # Get responses
    responses = db.query(SurveyResponse).filter(SurveyResponse.survey_id == survey_id).all()
    
    # Prepare data for export
    export_format = export_data.get("format", "excel")
    export_content = export_data.get("content", ["basic", "raw", "stats"])
    detail_level = export_data.get("detail", "detailed")
    
    if export_format == "excel":
        content, media_type = export_excel(survey, questions, responses, export_content, detail_level)
    elif export_format == "csv":
        content, media_type = export_csv(survey, questions, responses, export_content, detail_level)
    elif export_format == "html":
        content, media_type = export_html(survey, questions, responses, export_content, detail_level)
    else:
        raise HTTPException(status_code=400, detail="Invalid export format")
    
    # Set filename and encode it for headers
    filename = f"{survey.title}_分析结果.{export_format == 'excel' and 'xlsx' or export_format == 'csv' and 'csv' or 'html'}"
    import urllib.parse
    encoded_filename = urllib.parse.quote(filename)
    
    return FastAPIResponse(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
        }
    )

def export_excel(survey, questions, responses, export_content, detail_level):
    """Export data as Excel file"""
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Basic info sheet
        if "basic" in export_content:
            basic_data = {
                "Survey Title": [survey.title],
                "Description": [survey.description],
                "Status": [survey.status],
                "Created At": [survey.created_at.strftime("%Y-%m-%d %H:%M:%S")],
                "Total Responses": [len(responses)]
            }
            pd.DataFrame(basic_data).to_excel(writer, sheet_name="Basic Info", index=False)
        
        # Raw data sheet
        if "raw" in export_content:
            raw_data = []
            for response in responses:
                response_dict = {
                    "Response ID": response.id,
                    "Submitted At": response.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "IP Address": response.ip_address
                }
                # Add answers
                for answer in response.answers:
                    question = next((q for q in questions if q.id == answer.question_id), None)
                    if question:
                        response_dict[f"Q{question.order_index}: {question.title}"] = answer.text_answer or answer.rating_value
                raw_data.append(response_dict)
            pd.DataFrame(raw_data).to_excel(writer, sheet_name="Raw Data", index=False)
        
        # Statistics sheet
        if "stats" in export_content:
            stats_data = []
            for question in questions:
                question_answers = []
                for response in responses:
                    for answer in response.answers:
                        if answer.question_id == question.id:
                            question_answers.append(answer.text_answer or answer.rating_value)
                
                if question.type == "rating":
                    if question_answers:
                        ratings = [int(r) for r in question_answers if r]
                        if ratings:
                            stats_data.append({
                                "Question": f"Q{question.order_index}: {question.title}",
                            "Type": question.type,
                            "Average": sum(ratings) / len(ratings),
                                "Median": sorted(ratings)[len(ratings) // 2],
                                "Count": len(ratings)
                            })
                elif question.type in ["multiple_choice", "checkbox"]:
                    option_counts = {}
                    for answer in question_answers:
                        if isinstance(answer, list):
                            for option in answer:
                                option_counts[option] = option_counts.get(option, 0) + 1
                        else:
                            option_counts[answer] = option_counts.get(answer, 0) + 1
                    
                    for option, count in option_counts.items():
                        stats_data.append({
                            "Question": f"Q{question.order_index}: {question.title}",
                            "Type": question.type,
                            "Option": option,
                            "Count": count,
                            "Percentage": (count / len(responses)) * 100 if responses else 0
                        })
            pd.DataFrame(stats_data).to_excel(writer, sheet_name="Statistics", index=False)
    
    output.seek(0)
    return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def export_csv(survey, questions, responses, export_content, detail_level):
    """Export data as CSV file"""
    # For CSV, we'll export raw data only
    raw_data = []
    for response in responses:
        response_dict = {
            "Response ID": response.id,
            "Submitted At": response.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "IP Address": response.ip_address
        }
        # Add answers
        for answer in response.answers:
            question = next((q for q in questions if q.id == answer.question_id), None)
            if question:
                response_dict[f"Q{question.order_index}: {question.title}"] = answer.text_answer or answer.rating_value
        raw_data.append(response_dict)
    
    df = pd.DataFrame(raw_data)
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    return output.getvalue(), "text/csv"

def export_html(survey, questions, responses, export_content, detail_level):
    """Export data as HTML file"""
    # Create HTML content
    html_content = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{survey.title} - Analysis Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .section {{ margin-bottom: 30px; }}
            .stats {{ margin-top: 20px; }}
        </style>
    </head>
    <body>
        <h1>{survey.title}</h1>
        <p>{survey.description}</p>
    """
    
    # Basic info
    if "basic" in export_content:
        html_content += f"""
        <div class="section">
            <h2>Basic Information</h2>
            <table>
                <tr><th>Status</th><td>{survey.status}</td></tr>
                <tr><th>Created At</th><td>{survey.created_at.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
                <tr><th>Total Responses</th><td>{len(responses)}</td></tr>
            </table>
        </div>
        """
    
    # Statistics
    if "stats" in export_content:
        html_content += '<div class="section"><h2>Statistics</h2>'
        for question in questions:
            question_answers = []
            for response in responses:
                for answer in response.answers:
                    if answer.question_id == question.id:
                        question_answers.append(answer.text_answer or answer.rating_value)
            
            html_content += f"<h3>Q{question.order_index}: {question.title}</h3>"
            
            if question.type == "rating":
                if question_answers:
                    ratings = [int(r) for r in question_answers if r]
                    if ratings:
                        avg = sum(ratings) / len(ratings)
                        median = sorted(ratings)[len(ratings) // 2]
                        html_content += f"""
                        <div class="stats">
                            <p>Average: {avg:.2f}</p>
                            <p>Median: {median}</p>
                            <p>Count: {len(ratings)}</p>
                        </div>
                        """
            elif question.type in ["multiple_choice", "checkbox"]:
                option_counts = {}
                for answer in question_answers:
                    if isinstance(answer, list):
                        for option in answer:
                            option_counts[option] = option_counts.get(option, 0) + 1
                    else:
                        option_counts[answer] = option_counts.get(answer, 0) + 1
                
                html_content += '<table>'
                html_content += '<tr><th>Option</th><th>Count</th><th>Percentage</th></tr>'
                for option, count in option_counts.items():
                    percentage = (count / len(responses)) * 100 if responses else 0
                    html_content += f'<tr><td>{option}</td><td>{count}</td><td>{percentage:.2f}%</td></tr>'
                html_content += '</table>'
        html_content += '</div>'
    
    # Raw data
    if "raw" in export_content and detail_level == "detailed":
        html_content += '<div class="section"><h2>Raw Data</h2><table>'
        # Add headers
        headers = ["Response ID", "Submitted At", "IP Address"]
        for question in questions:
            headers.append(f"Q{question.order_index}: {question.title}")
        html_content += '<tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr>'
        
        # Add data rows
        for response in responses:
            row = [
                str(response.id),
                response.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                response.ip_address
            ]
            for question in questions:
                answer = next((a for a in response.answers if a.question_id == question.id), None)
                row.append(str(answer.text_answer or answer.rating_value) if answer else '')
            html_content += '<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>'
        html_content += '</table></div>'
    
    html_content += '</body></html>'
    
    # Return HTML content
    return html_content.encode('utf-8'), "text/html"
