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
        lines = source.readlines()
        date = ""
        data = []
        for line in lines:
            # Date information
            if line.startswith("*"):
                date = line.strip("*").strip()
            # Bowling information
            elif "bowling" in line and date != "":
                scores = []
                start = line.find("(") + 1
                end = line.find(")")
                if start != 0:
                    scores = line[start:end].split(",")
                    scores = list(map(int, scores))
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


if __name__ == "__main__":
    gen_plots()
