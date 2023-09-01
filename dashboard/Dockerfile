FROM python

WORKDIR /dashboard

#Copy over requirements file
COPY requirements.txt .

#Install the requirements
RUN pip3 install -r requirements.txt

#Transfer over Python dashboard file
COPY dashboard.py .

#Expose the port
EXPOSE 8501

CMD streamlit run dashboard.py
