# Makefile
.PHONY: init plan apply destroy fmt validate

ENV ?= dev

init:
	cd environments/$(ENV) && terraform init

plan:
	cd environments/$(ENV) && terraform plan

apply:
	cd environments/$(ENV) && terraform apply

destroy:
	cd environments/$(ENV) && terraform destroy

fmt:
	terraform fmt -recursive

validate:
	@for dir in environments/*/; do \
		echo "=== Validating $$dir ==="; \
		cd $$dir && terraform validate && cd ../..; \
	done

test:
	@for dir in modules/*/; do \
		if [ -d "$$dir/tests" ]; then \
			echo "=== Testing $$dir ==="; \
			cd $$dir && terraform test && cd ../..; \
		fi \
	done
