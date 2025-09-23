import argparse
import uvicorn
from fastapi import File, FastAPI, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from model import HeartRiskModel
from utils import drop_leak, fix_gender, check_file

app = FastAPI(title='FastAPI приложение для предсказания риска сердечного приступа')
model = HeartRiskModel()
templates = Jinja2Templates(directory="../templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    print(request)
    return templates.TemplateResponse(
        name="home_form.html",
        context={"request": request}
    )

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    # save_path = f"uploaded_{file.filename}"     # создаём имя файла, под которым хотим его сохранить на сервере
    # with open(save_path, "wb") as buffer:       # "w" — write, "b" — binary
        # shutil.copyfileobj(file.file, buffer)   # берем файл, который загрузил пользователь, и сохраняем его на сервере под именем save_path
    file_bytes = await file.read()
    try:
        df = check_file(file_bytes, file.filename)
    except ValueError as e:
        return templates.TemplateResponse(
            name="home_form.html",
            context={
                "request": request,
                "error_message": f"Ошибка: {str(e)}"}
        )
    try:
        risk = model.predict_risk(df)
    except Exception as e:
        return templates.TemplateResponse(
            name="home_form.html",
            context={
                "request": request,
                "error_message": f"Произошла ошибка при оценке риска: {str(e)}"
            }
        )

    return templates.TemplateResponse(          # после загрузки возвращаем форму снова с сообщением
        name="home_form.html",
        context={
            "request": request,
            "success_message": f"Файл {file.filename} успешно загружен!",
            "risk_message": f"Результат: <br>"
                            f"- Риск сердечного приступа оценивается в {round(risk['risk_prob']*100,1)} условных %. <br>"
                            f"- По текущему порогу ({risk['threshold']}) риск считается {"высоким." if risk['risk_bool'] else "низким."}"
        }
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()                                            # создаём "объект-парсер"
    parser.add_argument("--host", type=str, default="127.0.0.1")    # добавляем в него аргументы
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()                                                    # считываем аргументы из командной строки, сохраняем в объекте типа Namespace
    uvicorn.run("main:app", **vars(args))                                    # превращаем их в словарь + распаковываем в именованные параметры функции, запускает сервер на указанном хосте и порте