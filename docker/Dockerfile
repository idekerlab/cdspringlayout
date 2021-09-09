FROM continuumio/miniconda3

RUN conda install -y -c conda-forge networkx


RUN mkdir /tmp/cdspringlayout
COPY dist/*.whl /tmp/cdspringlayout

RUN /opt/conda/bin/pip install /tmp/cdspringlayout/cdspringlayout*whl

RUN rm -rf /tmp/cdspringlayout


ENTRYPOINT ["/opt/conda/bin/cdspringlayoutcmd.py"]
CMD ["--help"]
