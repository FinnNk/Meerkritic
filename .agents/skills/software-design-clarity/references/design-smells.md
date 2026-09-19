# Design Smells

Use these as prompts for investigation, not automatic defects.

## Shallow module

Symptoms:

- large interface;
- tiny implementation;
- callers still need detailed knowledge.

Question:

> What complexity does this module actually hide?

## Pass-through layer

Symptoms:

- same method names/arguments repeated through layers;
- intermediate object contributes no policy, abstraction, or information hiding.

## Configuration leakage

Symptoms:

- constructors/functions with many policy knobs;
- callers repeatedly pass the same values;
- options exist without demonstrated variability.

## Tactical special case

Symptoms:

- "temporary" flag;
- code path unique to one caller;
- branch added solely to satisfy a local test;
- duplicated logic instead of improving an abstraction.

## Knowledge leakage

Symptoms:

- caller must understand database schema, provider semantics, runtime internals, or file layout;
- several modules encode the same invariant.

## Abstraction duplication

Symptoms:

- two or more concepts represent the same lifecycle or responsibility under different names.

## Exception-as-normal-flow

Symptoms:

- exceptions represent not-applicable, cancelled, skipped, absent, deferred, or other expected outcomes.

## Obscure invariant

Symptoms:

- important rule exists only implicitly in implementation order or scattered conditionals;
- interface does not reveal a constraint callers must obey.

## Premature framework

Symptoms:

- generic extension points before a second concrete use;
- plugin systems with one implementation;
- abstractions built for imagined future requirements.

## Architecture theatre

Symptoms:

- many layers;
- many interfaces;
- dependency graph looks clean;
- cognitive burden remains unchanged or increases.

A compliant dependency graph is not by itself a good design.
