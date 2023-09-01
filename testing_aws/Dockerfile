FROM python

WORKDIR /dashboard/

COPY requirements.txt .

RUN  pip3 install -r requirements.txt

COPY main.py .

EXPOSE 8501

CMD streamlit run main.py
