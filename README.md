# Mapping Exploration Density at Continental Scale with Apache Sedona

Companion code for the Medium article on spatial drill hole analytics.

## Business context

Exploration portfolios contain millions of drill holes across hundreds of projects spanning decades. Mining companies inherit data from acquisitions, joint ventures, and historical operators. Each dataset uses different coordinate systems, depth conventions, and quality standards. Geologists need to answer: Where have we drilled? What's our actual data coverage? Which areas remain unexplored? Which zones need infill drilling for resource upgrade?

Large mineral properties often show biased drilling patterns: dense clusters around known zones, vast unexplored gaps elsewhere. High-grade zones may have drill spacing of 25-50 meters (excellent for resource estimation), while significant portions of the property have zero drilling within 2 km radius. Due diligence can reveal that only a fraction of a property has sufficient drill density for Indicated resource classification, while the majority remains Inferred or completely undrilled.

Traditional GIS software handles thousands of points but fails at millions; desktop analysis takes days; results go stale before publication.

## Disclaimer

Educational/demo code only. Not financial, safety, or engineering advice. Use at your own risk. Verify results independently before any production or operational use.

## License

MIT — see [LICENSE](LICENSE).