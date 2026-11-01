*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

Lumbre is a Día de los Muertos altar card. You type a name, a memory, and only the food, song, or object you actually know. An open-weight Gemma model writes the lines on the card. The memory you typed is kept word for word. A field you leave blank stays blank, and the model is not allowed to invent a favorite food or a story you did not tell.

## Demo

https://ashraf01k-lumbre.static.hf.space

The first card downloads Gemma 3 270M into the browser. There is a fictional example on the page if you do not want to write a real name.

## Code

https://github.com/AshrafGalaxy/lumbre

## How I Built It

The public altar is a static page. It loads `onnx-community/gemma-3-270m-it-ONNX` with Transformers.js and letters the card in the browser. The offering list is built from the form, not from the model's reply.

The Python package is the same scribe for a larger Gemma through the Hugging Face router (`google/gemma-3-4b-it`). That path needs Inference Providers credits. This account has none, and a free account cannot host a Docker Space, so the demo runs the small Gemma in the browser instead.

## Why Does Open Innovation Matter?

The weights are public, so the card is not locked to a closed chat API. The memory stays in the browser. A closed model would send that memory to a vendor's server, and the wording would disappear if the vendor changed the model or shut the endpoint down. Here the model id is one constant. The same page can point at another open instruct model.

## The Spirit of It

The useful part is the empty space. A remembrance is worse if the model invents a song or a Sunday that never happened. Lumbre puts your words on the altar and leaves the rest quiet.

## Prize Categories

Best Use of Gemma
