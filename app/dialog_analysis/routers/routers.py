# ЛОКАЛЬНЫЙ АНАЛИЗ ДИАЛОГА (ваш модуль dialog_analysis)
@app.post("/api/v1/analyze-dialog/local")
async def analyze_dialog_local(request: Dict[str, Any]):
    """Анализ диалога локальной логикой"""
    try:
        dialog_text = request.get("dialog", "")
        if not dialog_text:
            raise HTTPException(status_code=400, detail="Текст диалога обязателен")
        
        # Используем вашу локальную функцию анализа диалогов
        result = analyze_dialog(dialog_text)
        return {"service": "local", "result": result}
    except Exception as e:
        logger.error(f"Local dialog analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ВНЕШНИЙ АНАЛИЗ ДИАЛОГА (через LLM сервис)
@app.post("/api/v1/analyze-dialog/llm")
async def analyze_dialog_llm(request: Dict[str, Any]):
    """Анализ диалога через внешний LLM сервис"""
    try:
        dialog_text = request.get("dialog", "")
        context = request.get("context", "")
        
        if not dialog_text:
            raise HTTPException(status_code=400, detail="Текст диалога обязателен")
        
        prompt = f"""
        Проанализируй следующий диалог с собеседования и предоставь оценку:
        
        Контекст: {context}
        Диалог: {dialog_text}
        
        Проанализируй:
        1. Технические знания кандидата
        2. Коммуникативные навыки
        3. Сильные и слабые стороны
        4. Общая рекомендация
        """
        
        analysis = llm_client.chat(prompt)
        return {"service": "llm", "result": analysis}
    except Exception as e:
        logger.error(f"LLM dialog analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
