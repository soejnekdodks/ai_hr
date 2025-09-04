def main():
    # Загрузка конфигурации
    config = load_config('config/pipeline_config.yaml')
    
    # Инициализация пайплайна
    pipeline = CVParserPipeline(config)
    
    # Запуск мониторинга
    
    try:
        # Обработка данных
        for batch_results in pipeline.run():
            monitor.update_metrics(batch_results)
            
            # Сохранение результатов
            save_to_database(batch_results)
            
            # Логирование прогресса
            if monitor.metrics['processed'] % 1000 == 0:
                report = monitor.generate_report()
                logger.info(f"Progress report: {report}")
    
    except KeyboardInterrupt:
        logger.info("Pipeline stopped by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
    finally:
        # Финальный отчет
        final_report = generate_report()
        save_report(final_report)

if __name__ == "__main__":
    main()