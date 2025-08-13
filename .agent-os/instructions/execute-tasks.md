# Execute Tasks for Project Lily

## Overview
This document provides instructions for executing development tasks for Project Lily. It covers the development workflow, testing procedures, and quality gates.

## Development Workflow

### 1. Task Preparation
- Review the task requirements and acceptance criteria
- Understand the technical design and architecture
- Identify dependencies and potential risks
- Set up development environment

### 2. Implementation
- Follow the established code style and best practices
- Write tests alongside code (TDD preferred)
- Use type hints consistently
- Document public APIs and interfaces
- Commit frequently with descriptive messages

### 3. Testing
- Run unit tests: `just test`
- Run integration tests: `just test-integration`
- Run end-to-end tests: `just test-e2e`
- Ensure all tests pass before proceeding

### 4. Code Quality
- Run linting: `just lint`
- Run type checking: `just typecheck`
- Run formatting: `just format`
- Address all issues before submitting

### 5. Documentation
- Update relevant documentation
- Add code comments where needed
- Update API documentation if applicable
- Ensure examples are current and working

## Task Execution Checklist

### Before Starting
- [ ] Task requirements understood
- [ ] Development environment set up
- [ ] Dependencies identified
- [ ] Testing strategy planned
- [ ] Documentation plan created

### During Implementation
- [ ] Follow code style guidelines
- [ ] Write tests for new functionality
- [ ] Use type hints consistently
- [ ] Document public APIs
- [ ] Commit frequently with clear messages

### Before Submission
- [ ] All tests pass
- [ ] Code quality checks pass
- [ ] Documentation updated
- [ ] Performance impact assessed
- [ ] Security implications considered

### After Submission
- [ ] Code review completed
- [ ] Feedback addressed
- [ ] Integration tests pass
- [ ] Deployment successful
- [ ] Monitoring in place

## Testing Procedures

### Unit Testing
```bash
# Run all unit tests
just test

# Run specific test file
just test tests/unit/test_module.py

# Run tests with coverage
just test-cov

# Run tests in parallel
just test-parallel
```

### Integration Testing
```bash
# Run integration tests
just test-integration

# Run specific integration test
just test-integration tests/integration/test_feature.py
```

### End-to-End Testing
```bash
# Run end-to-end tests
just test-e2e

# Run specific e2e test
just test-e2e tests/e2e/test_workflow.py
```

### Performance Testing
```bash
# Run performance benchmarks
just test-benchmark

# Run specific benchmark
just test-benchmark tests/benchmark/test_performance.py
```

## Quality Gates

### Code Quality
- [ ] All linting checks pass
- [ ] Type checking passes
- [ ] Code formatting is correct
- [ ] No security vulnerabilities detected
- [ ] Code coverage meets minimum requirements

### Testing
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All end-to-end tests pass
- [ ] Performance benchmarks meet requirements
- [ ] No regressions introduced

### Documentation
- [ ] Public APIs documented
- [ ] User documentation updated
- [ ] Examples are current and working
- [ ] Migration guides created if needed
- [ ] Code comments are clear and helpful

### Security
- [ ] Security scan passes
- [ ] No sensitive data exposed
- [ ] Input validation implemented
- [ ] Access controls in place
- [ ] Error messages don't leak information

## Common Tasks

### Adding New Dependencies
1. Add to `pyproject.toml` in appropriate section
2. Update `uv.lock` with `uv lock`
3. Test that everything still works
4. Document why the dependency is needed

### Updating Configuration
1. Update configuration schema
2. Add validation rules
3. Update documentation
4. Test configuration loading
5. Provide migration guide if needed

### Adding New Commands
1. Create command implementation
2. Add tests for the command
3. Update command discovery
4. Add documentation
5. Test integration with shell

### Modifying AI Integration
1. Update AI client code
2. Add tests for new functionality
3. Update conversation management
4. Test with different models
5. Update documentation

## Troubleshooting

### Common Issues

#### Tests Failing
- Check if dependencies are up to date
- Verify test environment is correct
- Check for flaky tests
- Review recent changes

#### Linting Errors
- Run `just format` to fix formatting
- Address any remaining linting issues
- Check for unused imports
- Verify type hints are correct

#### Type Checking Errors
- Add missing type hints
- Fix incorrect type annotations
- Update type stubs if needed
- Check for `Any` usage

#### Performance Issues
- Profile the code to identify bottlenecks
- Optimize critical paths
- Check for memory leaks
- Review algorithm complexity

### Getting Help
- Check existing documentation
- Review similar implementations
- Ask for code review
- Create issue for complex problems

## Best Practices

### Code Organization
- Keep functions small and focused
- Use meaningful variable names
- Avoid code duplication
- Follow established patterns

### Testing
- Write tests for all new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests independent and fast

### Documentation
- Document public APIs clearly
- Include usage examples
- Keep documentation up to date
- Use consistent formatting

### Performance
- Profile before optimizing
- Use appropriate data structures
- Minimize memory allocations
- Cache frequently accessed data

### Security
- Validate all inputs
- Use secure defaults
- Follow principle of least privilege
- Log security events appropriately
