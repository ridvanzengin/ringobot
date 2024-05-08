#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import pandas as pd
from datetime import datetime
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# layout
xaxis_range = dict(
    rangeslider=dict(),
    type="date",
    rangeselector=dict(
        buttons=list([
            dict(count=1,
                 label="1d",
                 step="day",
                 stepmode="backward"),
            dict(count=3,
                 label="3d",
                 step="day",
                 stepmode="backward"),
            dict(count=7,
                 label="7d",
                 step="day",
                 stepmode="backward"),
            dict(count=30,
                 label="30d",
                 step="day",
                 stepmode="backward"),
            dict(step="all")
        ])
    )
)


def create_layout(xaxis_range, y_min, y_max, title=""):
    grapTempAcc = dict(
        data=[],
        layout=dict(
            title=title,
            showlegend=False,
            xaxis=xaxis_range,
            yaxis=dict(
                range=[y_min*0.97, y_max*1.03]
            ),
            yaxis2=dict(
                overlaying="y",
                side="right",
                range=[0, 4000]
            ),
            yaxis3=dict(
                overlaying="y",
                side="left",
                range=[0, 1.2]
            )
        )

    )
    return grapTempAcc


def priceLine(df):
    if "close" in df.columns:
        tempdf = df["close"]
        tempSerie = dict(
            x=tempdf.index,
            y=tempdf.values,
            type="scatter",
            name="temperature"
        )
        return tempSerie
    else:
        return None


def priceBar(df):
    if "close" in df.columns:
        tempdf = df["close"].resample("1d").mean()
        serieActivity = dict(
            x=tempdf.index,
            y=tempdf.values,
            color='yellow',
            opacity=0.45,
            type='bar',
            name="daily_price",
        )
        return serieActivity
    else:
        return None


def buySellPoints(session):
    buy_time = pd.Timestamp(session.buy_timestamp, unit="s") if session.buy_timestamp else None
    sell_time = pd.Timestamp(session.sell_timestamp, unit="s") if session.sell_timestamp else None
    buyDict = dict(
        x=[buy_time],
        y=[session.buy_price],
        mode='markers',
        marker=dict(
            size=20,
            color="green",
            symbol="triangle-up"
        ),
        name="buy"
    )
    sellDict = dict(
        x=[sell_time],
        y=[session.sell_price],
        mode='markers',
        marker=dict(
            size=20,
            color="red",
            symbol="triangle-down"
        ),
        name="sell"
    )
    return buyDict, sellDict



def createGraphs(session):
    df = session.data
    title = session.name
    min_close = df["close"].min()
    max_close = df["close"].max()
    grapTempAcc = create_layout(xaxis_range, min_close, max_close, title)
    grapTempAcc["data"].append(priceLine(df))
    grapTempAcc["data"].append(priceBar(df))
    buys, sells = buySellPoints(session)
    grapTempAcc["data"].append(buys)
    grapTempAcc["data"].append(sells)

    return grapTempAcc


def tempDiffLine(df):
    if "tempDiff3days_temp" in df.columns:
        tempDiffdf = df["tempDiff3days_temp"]
        #drop first 24 hours
        tempDiffdf = tempDiffdf[tempDiffdf.index > tempDiffdf.index[0] + pd.Timedelta(hours=24)]
        tempDiffSerie = dict(
            x=tempDiffdf.index,
            y=tempDiffdf.values + 0.5,
            type="scatter",
            name="tempDiff",
            yaxis="y3"
        )
        return tempDiffSerie
def accLine(df):
    if "xyz_std" in df.columns:
        accdf = df["xyz_std"]
        serieActivity = dict(
            x=accdf.index,
            y=accdf.values,
            color='yellow',
            mode="scatter",
            name="activity",
            yaxis="y2"
        )
        return serieActivity
    else:
        return None

def dailAccBar(df):
    dailyAcc = df["dailyAcc"].dropna() if "dailyAcc" in df else pd.DataFrame()
    # the mean of last 24h of accdf added to dailyDF as a new row
    accdfLast24HoursMean = df["xyz_std"][df["xyz_std"].index.max() - pd.Timedelta(hours=24): df["xyz_std"].index.max()].mean()

    df2BeAppended = pd.DataFrame([accdfLast24HoursMean], index=[df["xyz_std"].index.max().floor(freq="D")])
    dailyAcc = pd.concat([dailyAcc, df2BeAppended])
    dailyAcc.index = dailyAcc.index + pd.Timedelta(hours=12)
    dailyAcc.columns = ["dailyAcc"]
    dailyActivity = dict(
        x=dailyAcc.index,
        y=dailyAcc.dailyAcc * 4,
        color='yellow',
        opacity=0.45,
        type='bar',
        name="daily-acc",
        yaxis="y2"
    )
    return dailyActivity


def dailyTempBar(df):
    dailyTemp = df["dailyTemp"].dropna() if "dailyTemp" in df else pd.DataFrame()
    # the mean of last 24h of accdf added to dailyDF as a new row
    tempdfLast24HoursMean = df["temp"][df["temp"].index.max() - pd.Timedelta(hours=24): df["temp"].index.max()].mean()

    df2BeAppended = pd.DataFrame([tempdfLast24HoursMean], index=[df["temp"].index.max().floor(freq="D")])
    dailyTemp = pd.concat([dailyTemp, df2BeAppended])
    dailyTemp.index = dailyTemp.index + pd.Timedelta(hours=12)
    dailyTemp.columns = ["dailyTemp"]
    dailyTemperature = dict(
        x=dailyTemp.index,
        y=dailyTemp.dailyTemp,
        color='red',
        opacity=0.45,
        type='bar',
        name="daily-temp",
        yaxis="y"
    )
    return dailyTemperature




def heatDetectionPoints(animal=None):
    heatDetections = []
    if animal.session.events:
        heatevents = [animal.session.events.all_events[i].__dict__ for i in range(len(animal.session.events.all_events)) if animal.session.events.all_events[i].__dict__["event_type"] == "heat_detected"]
        heatDetections = [pd.Timestamp(heatevents[i]["timestamp"], unit="s") for i in range(len(heatevents))]
        daysago30 = pd.Timestamp.now() - pd.Timedelta(days=31)
        # if session is active and longer than 30 days, only show last 30 days
        if animal.session.session_state_id != 2 and animal.data.index.min() > daysago30:
            heatDetections = [heatDetections[i] for i in range(len(heatDetections)) if heatDetections[i] > daysago30]
    heatDetectionSeries = dict(
        x=heatDetections,
        y=[1.125] * len(heatDetections),
        mode="markers",
        name="heat",
        marker=dict(
            size=15,
            color="red",
            symbol="cross"
        ),
        yaxis="y3"
    )
    return heatDetectionSeries


def inseminationPoints(animal=None, session=None):
    inseminations = []
    if animal.session.events:
        ins_events = [animal.session.events.all_events[i].__dict__ for i in range(len(animal.session.events.all_events)) if animal.session.events.all_events[i].__dict__["event_type"] == "insemination_reported"]
        inseminations = [pd.Timestamp(ins_events[i]["timestamp"], unit="s") for i in range(len(ins_events))]
        daysago30 = pd.Timestamp.now() - pd.Timedelta(days=31)
        # if session is active and longer than 30 days, only show last 30 days
        if animal.session.session_state_id != 2 and animal.data.index.min() > daysago30:
            inseminations = [inseminations[i] for i in range(len(inseminations)) if inseminations[i] > daysago30]
    inseminationSeries = dict(
        x=inseminations,
        y=[1.125] * len(inseminations),
        mode="markers",
        name="insemination",
        marker=dict(
            size=15,
            color="green",
            symbol="star"
        ),
        yaxis="y3"
    )
    return inseminationSeries


def testBorders(grapTempAcc, session):
    testHeats = session.tests
    for i in range(len(testHeats)):
        print(testHeats[i].test_start, testHeats[i].test_end)
        if i % 2 == 0:
            color = 'rgba(108, 122, 137,0.2)'
        else:
            color = 'rgba(47,79,79,0.4)'
        testDict = dict(
            x=[testHeats[i].test_start, testHeats[i].test_end],
            y=[3000, 3000],
            fill='tozeroy',
            fillcolor=color,
            mode='none',
            name=f"test{i + 1}"
        )
        grapTempAcc["data"].append(testDict)
    return grapTempAcc

def heatBorders(grapTempAcc, session=None, heatTest=None):
    if session:
        heats = session.tests
    if heatTest:
        heats = [heatTest]
    for i in range(len(heats)):
        heatDict = dict(
            x=[heats[i].heat_start, heats[i].heat_end],
            y=[3000, 3000],
            fill='tozeroy',
            fillcolor='rgba(255,0,0,0.25)',
            mode='none',
            name=f"heat{i + 1}"
        )
        grapTempAcc["data"].append(heatDict)
    return grapTempAcc


def dueBorders(df):
    # change background of last 24 hours to red
    dueDict = dict(
        x=[df.index.max() - pd.Timedelta(hours=24), df.index.max()],
        y=[3500, 3500],
        fill='tozeroy',
        fillcolor='rgba(255,0,0,0.25)',
        mode='none',
        name="dueZone",
        yaxis="y2"
    )
    return dueDict


def heatProbLine(df):
    heatprobDF = pd.DataFrame(df["heatProb"].dropna().rolling(window=20).mean().fillna(0))
    heatprobDF = heatprobDF.resample("1H").mean()
    heatprobDF = heatprobDF[heatprobDF.values > 0.7]
    serieHeatProb = dict(
        x=heatprobDF.index,
        y=heatprobDF.heatProb + 0.03,
        mode='markers',
        marker=dict(
            size=10,
            color="blue",
            symbol="star"
        ),
        name='v1',
        type='scatter',
        yaxis="y3"
    )
    return serieHeatProb



def MLHeatProbLine(df):
    heatprobDF = pd.DataFrame(df["MLHeatProb"].dropna().rolling(window=20).mean().fillna(0))
    heatprobDF = heatprobDF.resample("1H").mean()
    heatprobDF = heatprobDF[heatprobDF.values > 0.7]
    serieHeatProb = dict(
        x=heatprobDF.index,
        y=heatprobDF.MLHeatProb + 0.07,
        mode='markers',
        marker=dict(
            size=8,
            color="black",
            symbol="diamond"
        ),
        name='ML',
        type='scatter',
        yaxis="y3"
    )
    return serieHeatProb
def heatProbBar(df):
    heatprobDF = pd.DataFrame(df["heatProb"].dropna().rolling(window=12).mean().fillna(0))
    dailyHeatProbDF = df["dailyHeatProb"].dropna() if "dailyHeatProb" in df else pd.DataFrame()
    probDF24HoursMean = heatprobDF[heatprobDF.index.max() - pd.Timedelta(hours=24): heatprobDF.index.max()].mean().values[0]
    df2BeAppended = pd.DataFrame([probDF24HoursMean], index=[heatprobDF.index.max().floor(freq="D")])
    dailyHeatProbDF = pd.concat([dailyHeatProbDF, df2BeAppended])
    dailyHeatProbDF.index = dailyHeatProbDF.index + pd.Timedelta(hours=12)
    dailyHeatProbDF.columns = ["dailyProb"]
    serieDailyHeatProb = dict(
        x=dailyHeatProbDF.index,
        y=dailyHeatProbDF.dailyProb + 0.03,
        color='red',
        opacity=0.45,
        type='bar',
        name='prob-level',
        yaxis="y3"
    )
    return serieDailyHeatProb

def dueProbLine(df):
    dueprobDF = pd.DataFrame(df["MLDueProb"].dropna().rolling(window=4).mean().fillna(0))
    dueprobDF = dueprobDF[dueprobDF.values > 0.55]
    serieDueProb = dict(
        x=dueprobDF.index,
        y=dueprobDF.MLDueProb + 0.03,
        mode='markers',
        marker=dict(
            size=10,
            color="blue",
            symbol="star"
        ),
        name='due',
        type='scatter',
        yaxis="y3"
    )
    return serieDueProb

def dueProbBar(df):
    dueprobDF = pd.DataFrame(df["MLDueProb"].dropna().rolling(window=4).mean().fillna(0))
    dailyDueProbDF = df["dailyDueProb"].dropna() if "dailyDueProb" in df else pd.DataFrame()
    probDF24HoursMean = dueprobDF[dueprobDF.index.max() - pd.Timedelta(hours=24): dueprobDF.index.max()].values.mean()
    df2BeAppended = pd.DataFrame([probDF24HoursMean], index=[dueprobDF.index.max().floor(freq="D")])
    dailyDueProbDF = pd.concat([dailyDueProbDF, df2BeAppended])
    dailyDueProbDF.index = dailyDueProbDF.index + pd.Timedelta(hours=12)
    dailyDueProbDF.columns = ["dailyProb"]
    serieDailyDueProb = dict(
        x=dailyDueProbDF.index,
        y=dailyDueProbDF.dailyProb + 0.03,
        color='red',
        opacity=0.45,
        type='bar',
        name='due-level',
        yaxis="y3"
    )
    return serieDailyDueProb

def t2cLine(df):
    if "t2c" in df:
        t2cDF = pd.DataFrame(df["t2c"].dropna().rolling(window=4).mean().resample("2H").mean().round())
        serieT2C = dict(
            x=t2cDF.index,
            y=[1.125] * len(t2cDF),
            text=t2cDF.t2c,
            mode='text',
            name='hours2calving',
            color="red",
            textfont=dict(
                family="sans serif",
                size=18,
                color="red"
            ),
            yaxis="y3"
        )
        return serieT2C


def createEstrousSessionGraph(session):
    grapTempAcc = create_layout(xaxis_range)
    df = session.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(accLine(df))
    grapTempAcc["data"].append(dailAccBar(df))
    grapTempAcc["data"].append(heatDetectionPoints(session=session))
    grapTempAcc["data"].append(inseminationPoints(session=session))
    grapTempAcc = heatBorders(grapTempAcc, session=session)
    grapTempAcc = testBorders(grapTempAcc, session=session)
    return grapTempAcc

def createEstrousAnimalGraph(animal):
    grapTempAcc = create_layout(xaxis_range)
    df = animal.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(accLine(df))
    grapTempAcc["data"].append(dailAccBar(df))
    grapTempAcc["data"].append(heatDetectionPoints(animal=animal))
    grapTempAcc["data"].append(inseminationPoints(animal=animal))
    grapTempAcc["data"].append(MLHeatProbLine(df)) if "MLHeatProb" in df.columns else []
    grapTempAcc["data"].append(heatProbBar(df)) if "heatProb" in df.columns else []
    return grapTempAcc

def createPregnancySessionGraph(session):
    grapTempAcc = create_layout(xaxis_range)
    df = session.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(tempDiffLine(df))
    grapTempAcc["data"].append(dailyTempBar(df))
    grapTempAcc["data"].append(dueProbLine(df))
    return grapTempAcc

def createPregnancyAnimalGraph(animal):
    grapTempAcc = create_layout(xaxis_range)
    df = animal.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(tempDiffLine(df))
    grapTempAcc["data"].append(dailyTempBar(df))
    grapTempAcc["data"].append(dueProbLine(df)) if "MLDueProb" in df.columns else []
    grapTempAcc["data"].append(dueProbBar(df)) if "MLDueProb" in df.columns else []
    grapTempAcc["data"].append(t2cLine(df)) if "t2c" in df.columns else []
    if animal.session.session_state_id == 2:
        grapTempAcc["data"].append(dueBorders(df))
    return grapTempAcc

def createHealthGraph(object):
    grapTempAcc = create_layout(xaxis_range)
    df = object.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(accLine(df))
    grapTempAcc["data"].append(dailAccBar(df))
    return grapTempAcc

def createHeatTestGraph(heatTest):
    grapTempAcc = create_layout(xaxis_range)
    df = heatTest.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(accLine(df))
    grapTempAcc["data"].append(dailAccBar(df))
    grapTempAcc = heatBorders(grapTempAcc, heatTest=heatTest)
    return grapTempAcc

def createDueTestGraph(dueTest):
    grapTempAcc = create_layout(xaxis_range)
    df = dueTest.data
    grapTempAcc["data"].append(tempLine(df))
    grapTempAcc["data"].append(tempDiffLine(df))
    grapTempAcc["data"].append(dailyTempBar(df))
    return grapTempAcc

def createChatGraph(data):
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.bar(data.index, data['dailyHeatProb'], alpha=0.5, color="blue")
    ax2 = ax.twinx()
    ax2.bar(data.index, data['dailyAcc'], alpha=0.5, color="green")
    ax.set_title(f"{data.customer_name[0]} - {data.animal_no[0]}", fontsize=20)
    ax2.set_ylim(0, 4000)
    ax.set_ylim(0, 1.3)
    plt.tight_layout()
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close(fig)
    return img_buf

def createDeviceGraph(df):
    grapTempAcc = dict(
        data=[],
        layout=dict(
            title="Temperature",
            xaxis=xaxis_range,
            yaxis=dict(
                range=[0, 40]
            ),
            yaxis2=dict(
                overlaying="y",
                side="right",
                range=[0, 4000]
            )
        )

    )

    ##### data ####

    # generic data
    tempSerie = dict(
        x=df.index,
        y=df["temp"],
        type="scatter",
        name="temperature"
    )
    grapTempAcc["data"].append(tempSerie)
    #print(accdf["value"].tail(5))
    serieActivity = dict(
        x=df.index,
        y=df["accelTotal"],
        color='yellow',
        mode="scatter",
        name="activity",
        yaxis="y2"
    )

    grapTempAcc["data"].append(serieActivity)

    return grapTempAcc