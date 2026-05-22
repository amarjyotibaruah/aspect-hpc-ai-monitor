"""AI-based diagnostic assistant for ASPECT simulation logs."""

import os
from openai import OpenAI
from openai import APIConnectionError, AuthenticationError, RateLimitError


class AIDiagnoser:
    """Use an AI model to diagnose ASPECT simulation issues."""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Missing OPENAI_API_KEY environment variable. "
                "Set it using: export OPENAI_API_KEY='your_key_here'"
            )

        self.client = OpenAI(api_key=api_key)

    def diagnose(self, log_summary, issue_summary):
        """Generate an AI diagnosis from parsed ASPECT log summaries."""

        prompt = f"""
You are an expert in ASPECT geodynamic simulations, HPC workflows, and nonlinear Stokes solver failures.

Analyze this ASPECT simulation summary.

Log summary:
{log_summary}

Detected issues:
{issue_summary}

Please provide:
1. Likely cause
2. Evidence from the log summary
3. Practical fixes
4. Suggested next run settings
5. Short final recommendation
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a computational geodynamics and HPC "
                            "simulation expert."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            return response.choices[0].message.content

        except AuthenticationError:
            return (
                "AI diagnosis unavailable: OpenAI authentication failed. "
                "Check your OPENAI_API_KEY."
            )

        except RateLimitError:
            return (
                "AI diagnosis unavailable: OpenAI API quota or rate limit was reached. "
                "Check your OpenAI billing, usage limits, or try again later."
            )

        except APIConnectionError:
            return (
                "AI diagnosis unavailable: Could not connect to OpenAI API. "
                "Check your internet connection."
            )

        except Exception as error:
            return f"AI diagnosis unavailable due to unexpected error: {error}"
