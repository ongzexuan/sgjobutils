# Utility Library for Processing and Extracting Features from Job Descriptions

This library is a small collection of re-usable functions to process job descriptions (mainly from Singapore).

All functions are relatively simple and involve the use of some hard-coded heuristics. The docstrings within the modules will provide more information about how the function was designed and intended to be used.

## Categories

### Education

The transformers reduce the educational qualification of the job description to one of the following in this list: degree, diploma, ITE, primary/secondary. Legacy versions had distinctions for 'primary' and 'secondary'. 

### Experience Level

The transformers reduce the experience level required of the job to one of the following: entry, manager, executive, professional, none. Note that this distinction is rather meaningless, except for the distinction between entry and non-entry level jobs.

## Common

This main module contains most of the helper functions needed.

## Money

This module handles money strings and extraction from descriptions. Generally not invoked directly, and is instead used through the main `common` module instead.

