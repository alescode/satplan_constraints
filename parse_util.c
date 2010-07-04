#include "num2sat.h"

#include "output.h"
#include "memory.h"

void print_tables (char* filename){
    FILE* OUT = NULL;
    int i, j;
    
    if ( (OUT = fopen(filename, "w")) == NULL ) {
        printf("\ncan't open file %s!\n\n",filename);
        exit( 1 );
    }
    
    if (gcmd_line.display_info == 103 ) {
        fprintf(OUT, "constants %d", gnum_constants);
        for ( i = 0; i < gnum_constants; i++ ) {
            fprintf(OUT, "\n%d %s", i, gconstants[i]);
        }
        
        fprintf(OUT, "\n\ntypes %d", gnum_types);
        for ( i = 0; i < gnum_types; i++ ) {
            fprintf(OUT, "\n%d %s ", i, gtype_names[i]);
            for ( j = 0; j < gtype_size[i]; j++ ) {
                fprintf(OUT, "%d ", gtype_consts[i][j]);
            }
        }
        
        fprintf(OUT, "\n\npredicates %d", gnum_predicates);
        for ( i = 0; i < gnum_predicates; i++ ) {
            fprintf(OUT, "\n%3d %s ", i, gpredicates[i]);
            for ( j = 0; j < garity[i]; j++ ) {
                fprintf(OUT, "%d ", gpredicates_args_type[i][j]);
            }
        }
        
        /*
        fprintf(OUT, "\n\nfunctions %d", gnum_functions);
        for ( i = 0; i < gnum_functions; i++ ) {
            fprintf(OUT, "\n%3d %s: ", i, gfunctions[i]);
            for ( j = 0; j < gf_arity[i]; j++ ) {
                fprintf(OUT, "%d ", gfunctions_args_type[i][j]);
            }
        }*/
        
        fprintf(OUT, "\n\nfacts %d", gnum_relevant_facts);
        for ( i = 0; i < gnum_relevant_facts; i++ ) {
            fprintf(OUT, "\n%d ", i);
            print_Fact_file(OUT, &(grelevant_facts[i]));
        }
        
        /*
        printf("\n\nfluents %d", gnum_relevant_fluents);
        for ( i = 0; i < gnum_relevant_fluents; i++ ) {
            printf("\n%d: ", i);
            print_Fluent( &(grelevant_fluents[i]) );
        }
        */
        fprintf(OUT, "\n\n");
    }
    
    fclose(OUT);
}