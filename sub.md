*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 4: Ghost in the Machine](https://dev.to/challenges/hacktoberfest-week4-2026-10-26)*

## What I Built

Lumbre is a Día de los Muertos altar card. You type a name, a memory, and only the food, song, or object you actually know. An open-weight Gemma model writes the lines on the card. The memory you typed is kept word for word. A field you leave blank stays blank, and the model is not allowed to invent a favorite food or a story you did not tell.

## Demo

https://ashraf01k-lumbre.static.hf.space

A card takes a few seconds. There is a fictional example on the page if you do not want to write a real name.

## Code

https://github.com/AshrafGalaxy/lumbre

## How I Built It

The public altar calls Llama 3.3 70B Instruct, an open-weight model, at an OpenAI-compatible host. The reply comes back in a few seconds. The offering list is built from the form, not from the model's reply. The same Python scribe can point at another open model, including Gemma through the Hugging Face router when that account has credits.

## Why Does Open Innovation Matter?

The weights are public, so the card is not locked to a closed chat API. The page does not download a model, and it does not hide a private key. A closed model would tie the wording to one vendor. Here the model id is one constant, and the same scribe can point at another open instruct model.

## The Spirit of It

The useful part is the empty space. A remembrance is worse if the model invents a song or a Sunday that never happened. Lumbre puts your words on the altar and leaves the rest quiet.
