@echo off
SET COUNT=1

:LOOP
echo Executando o teste pela %COUNT%ª vez...
pytest test_create_comprovante.py

IF %COUNT%==10 (
    echo Todas as 10 execuções foram concluídas.
    goto END
)

SET /A COUNT=%COUNT%+1
goto LOOP

:END
echo Script concluído.
pause
