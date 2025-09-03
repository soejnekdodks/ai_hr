# КОМБИНИРОВАННЫЙ АНАЛИЗ
@app.post("/api/v1/analyze-complete")
async def complete_analysis(
    file: UploadFile = File(None),
    request: Dict[str, Any] = None
):
    """Полный анализ: резюме + диалог"""
    try:
        results = {}
        
        # Анализ резюме (локальный)
        if file:
            file_content = await file.read()
            cv_result = analyze_cv_content(file_content)
            results["cv_analysis"] = {"service": "local", "result": cv_result}
        
        # Анализ диалога (LLM)
        if request and request.get("dialog"):
            dialog_text = request.get("dialog")
            context = request.get("context", "")
            
            prompt = f"""
            На основе резюме и диалога с собеседования, дай комплексную оценку кандидата.
            
            Резюме: {str(results.get('cv_analysis', {}).get('result', {}))}
            Диалог: {dialog_text}
            Контекст: {context}
            
            Проанализируй соответствие позиции и дай финальную рекомендацию.
            """
            
            dialog_result = llm_client.chat(prompt)
            results["dialog_analysis"] = {"service": "llm", "result": dialog_result}
        
        return results
        
    except Exception as e:
        logger.error(f"Complete analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Простой чат с LLM
@app.post("/api/v1/chat")
async def chat_with_ai(request: Dict[str, Any]):
    """Простой чат с внешним LLM"""
    try:
        message = request.get("message", "")
        if not message:
            raise HTTPException(status_code=400, detail="Сообщение обязательно")
        
        response = llm_client.chat(message)
        return {"response": response}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке запроса")