"""A convenient script to parse bowling scores and plot statistics."""

import datetime as dt
import json
import os

import click
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def extract_bowling_data(json_file, org_file):
    """Extract bowling data from org file into JSON."""
    with open(org_file, "r", encoding="utf8") as source:
        date, data, scores = "", [], []

        for line in source.readlines():
            # Date information encountered
            if line.startswith("*"):
                if scores:
                    data.append({"date": date, "scores": scores})
                    scores = []
                date = line.strip("*").strip()
            # Bowling information encountered
            elif all(token in line for token in ["bowling", "(", ")"]) and date != "":
                start = line.find("(") + 1
                end = line.find(")")
                if start != 0:
                    scores.extend(map(int, line[start:end].split(",")))

        # Handle final scores
        if scores:
            data.append({"date": date, "scores": scores})

        with open(json_file, "w", encoding="utf8") as output:
            json.dump(data, output)


def gen_stats(data):
    """Generate statistics from raw JSON data."""
    df = pd.DataFrame(data)
    df["date"] = df["date"].apply(lambda x: dt.datetime.strptime(x, "%b %d, %Y"))
    df.sort_values(by="date", inplace=True)

    df["min"] = df["scores"].apply(np.min)
    df["max"] = df["scores"].apply(np.max)
    df["mean"] = df["scores"].apply(np.mean)
    df["std"] = df["scores"].apply(np.std)
    df["cum_avg"] = df["mean"].cumsum() / range(1, df.shape[0] + 1)
    df["moving_avg"] = df["mean"].rolling(3, min_periods=1).mean()

    return df


def gen_scatter_plot(df, output_dir):
    """Generate scatter plot of all scores."""
    _, ax = plt.subplots(figsize=(10, 6))
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.title("All Scores")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
    ax.xaxis.set_tick_params(rotation=30)
    ax.xaxis.axis_date()
    plt.grid(alpha=0.1, axis="y", color="black", linestyle="-", linewidth=1)
    for _, (date, scores) in df[["date", "scores"]].iterrows():
        plt.scatter([date] * len(scores), scores, color="black")
    plt.subplots_adjust(bottom=0.20)
    plt.savefig(os.path.join(output_dir, "scatter_plot.png"), dpi=300)


def gen_errorbar_plot(df, output_dir):
    """Generate plot of mean scores with error bars."""
    _, ax = plt.subplots(figsize=(10, 6))
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.title("Average Scores")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
    ax.xaxis.set_tick_params(rotation=30)
    ax.xaxis.axis_date()
    plt.grid(alpha=0.1, axis="y", color="black", linestyle="-", linewidth=1)
    plt.errorbar(
        df["date"],
        df["mean"],
        df["std"],
        capsize=3,
        capthick=1,
        color="black",
        elinewidth=1,
        marker="o",
        markersize=3,
    )
    plt.subplots_adjust(bottom=0.20)
    plt.savefig(os.path.join(output_dir, "errorbar_plot.png"), dpi=300)


def gen_summary_plot(df, output_dir):
    """Generate summary plot of min, mean, and max scores."""
    _, ax = plt.subplots(figsize=(10, 6))
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.title("Summary")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
    ax.xaxis.set_tick_params(rotation=30)
    ax.xaxis.axis_date()
    plt.grid(alpha=0.1, axis="y", color="black", linestyle="-", linewidth=1)
    plt.plot(df["date"], df["min"], "r-", label="min")
    plt.plot(df["date"], df["mean"], "b-", label="mean")
    plt.plot(df["date"], df["max"], "g-", label="max")
    plt.legend()
    plt.subplots_adjust(bottom=0.20)
    plt.savefig(os.path.join(output_dir, "summary_plot.png"), dpi=300)


def gen_league_plot(df, output_dir):
    """Generate summary plot of league scores."""
    _, ax = plt.subplots(figsize=(10, 6))
    plt.xlabel("Date")
    plt.ylabel("Score")
    plt.title("League Summary")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=2))
    ax.xaxis.set_tick_params(rotation=30)
    plt.grid(alpha=0.1, axis="y", color="black", linestyle="-", linewidth=1)
    plt.errorbar(
        df["date"], df["cum_avg"], alpha=0.5, color="blue", linestyle="-", linewidth=0.9
    )
    plt.errorbar(
        df["date"],
        df["moving_avg"],
        alpha=0.5,
        color="green",
        linestyle="-",
        linewidth=0.9,
    )
    plt.errorbar(
        df["date"],
        df["mean"],
        [df["mean"] - df["min"], df["max"] - df["mean"]],
        capsize=3,
        capthick=1,
        color="black",
        elinewidth=1,
        linestyle=":",
        marker="o",
        markersize=3,
    )
    for idx, row in df.iterrows():
        offset = (
            4
            if idx + 1 < df.shape[0] and df.loc[idx + 1, "mean"] < row["mean"]
            else -11
        )
        plt.annotate(
            round(row["mean"]),
            (mdates.date2num(row["date"]), row["mean"]),
            xytext=(3, offset),
            textcoords="offset points",
        )
    plt.subplots_adjust(bottom=0.15)
    plt.savefig(os.path.join(output_dir, "league_plot.png"), dpi=300)


@click.command()
@click.argument("json-file", type=click.Path())
@click.option(
    "-d",
    "--output-dir",
    default="output",
    type=click.Path(),
    help="Path to output directory.",
)
@click.option(
    "-o",
    "--org-file",
    default="",
    type=click.Path(),
    help="Path to org file with bowling data. If this option is provided, a "
    "JSON file with the name `JSON_FILE' will be generated and used. If this "
    "option is not provided, data will be read from `JSON_FILE'.",
)
def gen_plots(json_file, output_dir, org_file):
    """
    Given a JSON file containing bowling data, generate plots analyzing the
    data. The JSON file can be generated from an org file.
    """
    if org_file:
        extract_bowling_data(json_file, org_file)

    with open(json_file, "r", encoding="utf8") as data:
        df = gen_stats(json.load(data))

    os.makedirs(output_dir, exist_ok=True)

    gen_scatter_plot(df, output_dir)
    gen_errorbar_plot(df, output_dir)
    gen_summary_plot(df, output_dir)
    gen_league_plot(df, output_dir)


if __name__ == "__main__":
    gen_plots()
